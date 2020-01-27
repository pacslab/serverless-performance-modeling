#!python
from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS, cross_origin

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
