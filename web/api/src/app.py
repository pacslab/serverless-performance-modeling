#!python
from flask import Flask, jsonify, request, abort, make_response, Response
from flask_cors import CORS, cross_origin

# for plots
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

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
    return pd.Series(props)


def plot_configs(ylab):
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.xlabel("Arrival Rate (reqs/s)")
    plt.ylabel(ylab)
    plt.gcf().subplots_adjust(left=0.12, bottom=0.25)


@app.route('/perfmodel/api/plots/pcold-arrival.png', methods=['GET'])
@cross_origin()
def pcold_plot_arrival_rate():
    required_params = ['idleBeforeExp', 'warmServiceTime',
                       'coldServiceTime']
    for required_param in required_params:
        if not request.args.get(required_param):
            abort(400)

    idleBeforeExp = float(request.args.get('idleBeforeExp'))
    warmServiceTime = float(request.args.get('warmServiceTime'))
    coldServiceTime = float(request.args.get('coldServiceTime'))

    params = {
        "arrival_rate": np.logspace(-3, 2, num=10),
        "warm_service_time": warmServiceTime,
        "cold_service_time": coldServiceTime,
        "idle_time_before_kill": idleBeforeExp,
    }
    df = pd.DataFrame(data=params)
    df = pd.concat([df, df.apply(analyze_sls, axis=1)], axis=1)

    # Cold Start Probability
    fig = plt.figure(figsize=(14, 4))
    plt.semilogx(df['arrival_rate'], df['cold_prob'] * 100)

    plot_configs("Cold Start Prob (%)")

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/perfmodel/api/plots/rt-arrival.png', methods=['GET'])
@cross_origin()
def rt_plot_arrival_rate():
    required_params = ['idleBeforeExp', 'warmServiceTime',
                       'coldServiceTime']
    for required_param in required_params:
        if not request.args.get(required_param):
            abort(400)

    idleBeforeExp = float(request.args.get('idleBeforeExp'))
    warmServiceTime = float(request.args.get('warmServiceTime'))
    coldServiceTime = float(request.args.get('coldServiceTime'))

    params = {
        "arrival_rate": np.logspace(-3, 2, num=10),
        "warm_service_time": warmServiceTime,
        "cold_service_time": coldServiceTime,
        "idle_time_before_kill": idleBeforeExp,
    }
    df = pd.DataFrame(data=params)
    df = pd.concat([df, df.apply(analyze_sls, axis=1)], axis=1)

    # Cold Start Probability
    fig = plt.figure(figsize=(14, 4))
    plt.semilogx(df['arrival_rate'], df['avg_resp_time'])

    plot_configs("RT (s)")

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


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

    return jsonify({
        'Idle Before Expiry': idleBeforeExp,
        'Warm Service Time': warmServiceTime,
        'Cold Service Time': coldServiceTime,
        'Arrival Rate': arrivalRate,
        'Average Server Count': props['avg_server_count'],
        'Average Utilization': props['avg_utilization'],
        'Average Running Instances': props['avg_running_count'],
        'Average Running Instances (warm)': props['avg_running_warm_count'],
        'AverageIdleInstances': props['avg_idle_count'],
        'Probability of Cold Start': props['cold_prob'],
    })


if __name__ == '__main__':
    app.run(debug=True)
