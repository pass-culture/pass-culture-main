import simplejson as json
import os, sys
import requests
import math

def main():

    if len(sys.argv) < 2:
        print('You need to pass at least one argument: report path')
        sys.exit(1)
    else:
        report_path = sys.argv[1]

    with open(report_path) ss json_file:
        data = json.load(json_file)

    endpoints_latency = _get_endpoint_latencies(data)

    recommendation = _get_search_endpoint_stats(data)

    endpoints_latency.append(recommendation['keywords_stats'])

    endpoints_over_limit = _verify_latency_is_not_over_limit(endpoints_latency)

    endpoints_summary = _get_endpoint_summary(endpoints_latency)

    error_codes = _get_error_codes(data)

    _send_to_ops_bot(endpoints_summary, recommendation['keyword_max'], error_codes)

    sys.exit(endpoints_over_limit)


def _get_endpoint_latencies(data):
    endpoints_latency = []
    endpoints_latency.append({'endpoint_name': 'Global', 'median': data['aggregate']['latency']['median'],
                              'p99': data['aggregate']['latency']['p99']})
    endpoints_latency.append(
        {'endpoint_name': '/users/signin', 'median': data['aggregate']['customStats']['/users/signin']['median'],
         'p99': data['aggregate']['customStats']['/users/signin']['p99']})
    endpoints_latency.append(
        {'endpoint_name': '/recommendations', 'median': data['aggregate']['customStats']['/recommendations']['median'],
         'p99': data['aggregate']['customStats']['/recommendations']['p99']})

    return endpoints_latency


def _get_error_codes(data):
    error_codes = []
    for key in data['aggregate']['codes'].keys():
        error_codes.append(key + ': ' + str(data['aggregate']['codes'][key]))

    return error_codes


def _verify_latency_is_not_over_limit(endpoints_latency):

    maximum_median_authorized_duration = os.environ.get('MAXIMUM_MEDIAN_AUTHORIZED_DURATION', 60000)
    maximum_p99_authorized_duration = os.environ.get('MAXIMUM_P99_AUTHORIZED_DURATION', 60000)

    endpoints_over_limit = False

    for endpoint in endpoints_latency:
        if endpoint['median'] > float(maximum_median_authorized_duration):
            print('Endpoint\'s median over maximum :', endpoint['endpoint_name'])
            endpoints_over_limit = True
        if endpoint['p99'] > float(maximum_p99_authorized_duration):
            print('Endpoint\'s P99 over maximum :', endpoint['endpoint_name'])
            endpoints_over_limit = True
    return endpoints_over_limit


def _get_endpoint_summary(endpoints_latency):
    endpoints_summary = ''
    for endpoint in endpoints_latency:
        endpoints_summary += '\\n *' + endpoint['endpoint_name'] + '* _Median_ : ' + str(
            endpoint['median']) + ' -  P99_ : ' + str(endpoint['p99'])
    return endpoints_summary


def _percentile(data, percentile):
    data = sorted(data)
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]


def _get_search_endpoint_stats(data):
    recommendation_keyword = []
    recommendation = {'keywords_stats': {}, 'keyword_max': {'keyword': '', 'value': 0}}
    data_custom_stats = data['aggregate']['customStats']

    for key in data_custom_stats.keys():
        if '/recommendations?keywords=' in key:
            recommendation_keyword.append(data_custom_stats[key]['max'])

            if data_custom_stats[key]['max'] > recommendation['keyword_max']['value']:
                recommendation['keyword_max']['value'] = data_custom_stats[key]['max']
                recommendation['keyword_max']['keyword'] = key

    recommendation['keywords_stats'] = {'endpoint_name': '/recommendations?keyword',
                                     'median': _percentile(recommendation_keyword, 50),
                                     'p99': _percentile(recommendation_keyword, 99)}

    return recommendation


def _send_to_ops_bot(endpoints_summary, recommendation_keyword_max, error_codes):
    slack_ops_bot_url = os.environ.get('SLACK_OPS_BOT_URL')

    headers = {
        'Content-type': 'application/json',
    }
    data = '{"text":"*Performance results* :' \
           + endpoints_summary + '\\n */recommendations?keyword* _Max Value _ : ' + str(
        recommendation_keyword_max['value']) \
           + ' - _for keyword_ :*' + recommendation_keyword_max['keyword'] + '*' + \
           '\\n *Return Codes :* ' + ", ".join(error_codes) + \
           '"}'
    requests.post(slack_ops_bot_url, headers=headers, data=data)


if __name__ == "__main__":
    main()
