import simplejson as json
import numpy as np

with open('reports/report-2019-11-12T09:31:02Z.json') as json_file:
    data = json.load(json_file)
    print(data['aggregate']['timestamp'])
    print(data['aggregate']['latency']['median'])
    print(data['aggregate']['latency']['p99'])

    for key in data['aggregate']['codes'].keys():
        if key != '200':
            print(key, data['aggregate']['codes'][key])

    print(data['aggregate']['customStats']['/users/signin']['median'])
    print(data['aggregate']['customStats']['/users/signin']['p99'])
    print(data['aggregate']['customStats']['/recommendations']['median'])
    print(data['aggregate']['customStats']['/recommendations']['p99'])

    recommendation_keyword_max = {'keyword': '', 'value': 0}
    recommendation_keywords = []

    for key in data['aggregate']['customStats'].keys():
        if '/recommendations?keywords=' in key:
            recommendation_keywords.append(data['aggregate']['customStats'][key]['max'])

            if data['aggregate']['customStats'][key]['max'] > recommendation_keyword_max['value']:
                recommendation_keyword_max['value'] = data['aggregate']['customStats'][key]['max']
                recommendation_keyword_max['keyword'] = key

    print('max value', recommendation_keyword_max['value'], 'for keyword ', recommendation_keyword_max['keyword'])

    p = np.percentile(recommendation_keywords, 99)
    print('percentile 99', p)
