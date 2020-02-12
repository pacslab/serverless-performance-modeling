"""
.. module:: perfmodel
   :platform: Unix, Windows
   :synopsis: A module for calculating the performance metrics of serverless computing.

.. moduleauthor:: Nima Mahmoudi <nma@ieee.org>


"""

# For computing the blocking probability
from scipy.stats import expon
import numpy as np
from math import factorial, inf, exp


def ErlangB(Rho, m):
    """ErlangB calculates the blocking probability for a M/G/m/m loss system.
    The probability returned is in range [0-1].
    It is easy to prove the correctness of the value.

    Source1: https://en.wikipedia.org/wiki/Erlang_%28unit%29#Erlang_B_formula

    Source2: https://stackoverflow.com/questions/23528145/how-to-wtite-erlang-b-and-erlang-c-formulas-in-python

    :param Rho: Rho = lambda/mu
    :type Rho: double
    :param m: The number of servers.
    :type m: int
    :return: The blocking probability for incoming requests.
    :rtype: double
    """
    InvB = 1.0
    for j in range(1, m+1):
        InvB = 1.0 + InvB * (j/Rho)
    return (1.0 / InvB)


def print_props(props):
    print("\nProperties:")
    print("------------------")
    for k in props.keys():
        print(f"{k}: {props[k]:4.6f}")
    print("------------------\n")


def get_sls_warm_count_dist(arrival_rate, warm_service_time, cold_service_time, idle_time_before_kill, maximum_concurrency=1000, faster_solution=True):
    warm_service_rate = 1 / warm_service_time
    cold_service_rate = 1 / cold_service_time
    rho = arrival_rate / warm_service_rate

    server_max = maximum_concurrency
    if faster_solution:
        server_max = min(30, maximum_concurrency)
    server_count = 0

    pblock_old = 1
    kill_rate = 0

    server_counts = [0]
    block_rates = [arrival_rate]
    kill_rates = [0.0]
    cold_probs = [1]
    running_counts = [arrival_rate * 1 * cold_service_time]
    running_warm_counts = [0]
    resp_times = [cold_service_time]


    while server_count < server_max:
        server_count += 1

        # The blocking probability, the blocked requests are cold starts.
        prob_block = ErlangB(rho, server_count)
        block_rate = prob_block * arrival_rate

        # The difference between blocked requests in m-1 and m is the requests
        # served on the m'th servers.
        prob_mth_server = pblock_old - prob_block
        pblock_old = prob_block

        # prob of no request in the next idle_time_before_kill for each request
        prob_kill_mth = 1 - \
            expon.cdf(idle_time_before_kill, scale=1 /
                      (arrival_rate * prob_mth_server))
        if prob_kill_mth > 0:
            # expected number of requests before the last one
            exp_request_before_kill = 1 / prob_kill_mth

            L = arrival_rate * prob_mth_server
            T = idle_time_before_kill + warm_service_time
            # average time between requests, when those requests wouldn't
            # be so far apart that results in killing the container.
            avg_inter_arrival = (-1 * T * exp(-1 * L * T)) + \
                (1 - exp(-1 * L * T)) / L

            # Time it takes for a container to be killed after being created.
            inter_kill_time = idle_time_before_kill + \
                (exp_request_before_kill - 1) * avg_inter_arrival
            kill_rate += 1 / inter_kill_time
        else:
            kill_rate += 0

        # Average number of warm containers serving the requests
        running_count_warm = arrival_rate * \
            (1 - prob_block) * warm_service_time
        running_count_cold = arrival_rate * prob_block * cold_service_time
        running_count = running_count_warm + running_count_cold

        # Average Response Time
        resp_time = (prob_block * cold_service_time) + \
            ((1 - prob_block) * warm_service_time)

        # If we reached maximum concurrency, we don't have cold starts any more!
        if server_count == maximum_concurrency:
            resp_time = warm_service_time
            running_count_cold = 0
            running_count = running_count_warm

        # Record properties for each state in CTMC
        server_counts.append(server_count)
        block_rates.append(block_rate)
        kill_rates.append(kill_rate)
        cold_probs.append(prob_block)
        running_counts.append(running_count)
        resp_times.append(resp_time)
        running_warm_counts.append(running_count_warm)

        if faster_solution:
            if block_rate > kill_rate:
                server_max = min(server_count + 30, maximum_concurrency)

    server_counts = np.array(server_counts)
    block_rates = np.array(block_rates)
    kill_rates = np.array(kill_rates)
    cold_probs = np.array(cold_probs)
    running_counts = np.array(running_counts)
    resp_times = np.array(resp_times)
    running_warm_counts = np.array(running_warm_counts)

    # if hasn't reached maximum concurrency, we can't measure it via float (accuracy is not enough, out guess is zero)
    rejection_prob = 0
    rejection_rate = 0
    # when we reach maximum concurrency, cold starts can't happen, so they are rejections
    if server_max == maximum_concurrency:
        rejection_prob = cold_probs[-1]
        cold_probs[-1] = 0
        rejection_rate = block_rates[-1]
        block_rates[-1] = 0

    states_counts = len(server_counts)
    Q = np.zeros((states_counts, states_counts))
    for i in range(states_counts):
        out_rate = 0
        if i > 0:
            Q[i, i-1] = kill_rates[i]
            out_rate += kill_rates[i]
        if i < states_counts-1:
            Q[i, i+1] = block_rates[i]
            out_rate += block_rates[i]
        Q[i, i] = 0 - out_rate

    Q[:, 0] = 1
    y = np.zeros((1, Q.shape[0]))
    y[0, 0] = 1

    solution = np.linalg.solve(np.array(Q.T), np.array(y.T))
    solution = solution.reshape(solution.shape[0],)
    solution[solution < 0] = 0

    avg_server_count = np.dot(server_counts, solution)
    avg_running_count = np.dot(running_counts, solution)
    avg_running_warm_count = np.dot(running_warm_counts, solution)
    avg_resp_time = np.dot(resp_times, solution)
    avg_idle_count = avg_server_count - avg_running_warm_count
    cold_prob = np.dot(cold_probs, solution)
    avg_utilization = avg_running_warm_count / avg_server_count

    return {
        "avg_server_count": avg_server_count,
        "avg_running_count": avg_running_count,
        "avg_running_warm_count": avg_running_warm_count,
        "avg_idle_count": avg_idle_count,
        "cold_prob": cold_prob,
        "avg_utilization": avg_utilization,
        "avg_resp_time": avg_resp_time,
        "rejection_prob": rejection_prob,
        "rejection_rate": rejection_rate,
    }, {
        "steady_state_probs": solution,
        "server_counts": server_counts,
    }
