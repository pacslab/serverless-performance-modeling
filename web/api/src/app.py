#!python
import copy

from flask import Flask, jsonify, request, abort, make_response, Response
from flask_cors import CORS, cross_origin

import numpy as np

from pacsltk import perfmodel

app = Flask(__name__, static_url_path='')
cors = CORS(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad input'}), 400)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Server error'}), 500)


def analyze_sls(row):
    props, _ = perfmodel.get_sls_warm_count_dist(**row)
    return props
    

@app.route('/')
def index():
    return jsonify({
        'msg': 'Welcome to serverless performance modelling!'
    })
    

@app.route('/perfmodel/api/props', methods=['POST'])
@cross_origin()
def get_props():
    required_params = ['idleBeforeExp', 'warmServiceTime',
                       'coldServiceTime', 'arrivalRate']
    if not request.json:
        abort(400)

    for required_param in required_params:
        if required_param not in request.json:
            abort(400)

    idleBeforeExp = float(request.json['idleBeforeExp'])
    warmServiceTime = float(request.json['warmServiceTime'])
    coldServiceTime = float(request.json['coldServiceTime'])
    arrivalRate = float(request.json['arrivalRate'])
    if arrivalRate > 100:
        abort(400)

    props, _ = perfmodel.get_sls_warm_count_dist(arrival_rate=arrivalRate,
                                                 warm_service_time=warmServiceTime,
                                                 cold_service_time=coldServiceTime,
                                                 idle_time_before_kill=idleBeforeExp)


    # for plots
    arrival_rates_plot = np.logspace(-3, 2, num=10)
    params = {
        "arrival_rate": 1,
        "warm_service_time": warmServiceTime,
        "cold_service_time": coldServiceTime,
        "idle_time_before_kill": idleBeforeExp,
    }
    plot_params = [copy.deepcopy(params) for _ in arrival_rates_plot]
    [plot_params[i].update({'arrival_rate': arrival_rates_plot[i]}) for i in range(len(arrival_rates_plot))]
    plot_props = [analyze_sls(p) for p in plot_params]

    plot_results = {}
    for k in plot_props[0]:
        plot_results[k] = [p[k] for p in plot_props]

    plot_results.update(params)
    plot_results.update({
        'arrival_rate': list(arrival_rates_plot),
    })


    return jsonify({
        'Idle Before Expiry': idleBeforeExp,
        'Warm Service Time': warmServiceTime,
        'Cold Service Time': coldServiceTime,
        'Arrival Rate': arrivalRate,
        'Average Server Count': props['avg_server_count'],
        'Average Utilization': props['avg_utilization'],
        'Average Running Instances': props['avg_running_count'],
        'Average Running Instances (warm)': props['avg_running_warm_count'],
        'Average Idle Instances': props['avg_idle_count'],
        'Average Response Time': props['avg_resp_time'],
        'Probability of Cold Start': props['cold_prob'],
        'Probability of Rejection': props['rejection_prob'],
        'Rate of Rejection': props['rejection_rate'],
        'plot_vals': plot_results,
    })


if __name__ == '__main__':
    app.run(debug=True)
