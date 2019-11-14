import simplejson as json
import os, sys
import requests
import math


def _percentile(data, percentile):
    data = sorted(data)
    size = len(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]


def _get_recommendation_keywords_stats():
    recommendation_keywords = []
    for key in data['aggregate']['customStats'].keys():
        if '/recommendations?keywords=' in key:
            recommendation_keywords.append(data['aggregate']['customStats'][key]['max'])

            if data['aggregate']['customStats'][key]['max'] > recommendation_keyword_max['value']:
                recommendation_keyword_max['value'] = data['aggregate']['customStats'][key]['max']
                recommendation_keyword_max['keyword'] = key

    recommendation_keywords_stats = {'endpoint_name': '/recommendations?keyword',
                            'median': _percentile(recommendation_keywords, 50),
                            'p99': _percentile(recommendation_keywords, 99)}

    return recommendation_keywords_stats


if len(sys.argv) < 2:
    print('You need to pass at least one argument: report path')
    sys.exit(1)
else:
    report_path = sys.argv[1]


def _send_to_ops_bot():
    global data
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

with open(report_path) as json_file:
    data = json.load(json_file)
    slack_ops_bot_url = os.environ.get('SLACK_OPS_BOT_URL')
    maximum_median_authorized_duration = os.environ.get('MAXIMUM_MEDIAN_AUTHORIZED_DURATION') or 60000
    maximum_p99_authorized_duration = os.environ.get('MAXIMUM_P99_AUTHORIZED_DURATION') or 60000

    error_codes = []
    for key in data['aggregate']['codes'].keys():
        error_codes.append(key + ': '+ str(data['aggregate']['codes'][key]))

    endpoints_latency = []

    endpoints_latency.append({'endpoint_name': 'Global', 'median': data['aggregate']['latency']['median'],
                'p99': data['aggregate']['latency']['p99']})

    endpoints_latency.append({'endpoint_name': '/users/signin', 'median': data['aggregate']['customStats']['/users/signin']['median'],
                  'p99': data['aggregate']['customStats']['/users/signin']['p99']})

    endpoints_latency.append({'endpoint_name': '/recommendations','median': data['aggregate']['customStats']['/recommendations']['median'],
                        'p99': data['aggregate']['customStats']['/recommendations']['p99']})

    recommendation_keyword_max = {'keyword': '', 'value': 0}

    endpoints_latency.append(_get_recommendation_keywords_stats())
    endpoints_summary = ''
    endpoints_over_limit = False

    for endpoint in endpoints_latency:
        endpoints_summary += '\\n *' + endpoint['endpoint_name'] + '* _Median_ : ' + str(endpoint['median']) + ' -  P99_ : ' + str(endpoint['p99'])
        if endpoint['median'] > float(maximum_median_authorized_duration):
            print('Endpoint\'s median over maximum :', endpoint['endpoint_name'])
            endpoints_over_limit = True
        if endpoint['p99'] > float(maximum_p99_authorized_duration):
            print('Endpoint\'s P99 over maximum :', endpoint['endpoint_name'])
            endpoints_over_limit = True

    _send_to_ops_bot()

sys.exit(endpoints_over_limit)
