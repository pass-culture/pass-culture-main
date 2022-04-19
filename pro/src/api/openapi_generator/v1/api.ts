import Package from '../../../../package.json'
import { API_URL } from 'utils/config'

import { Configuration, ConfigurationParameters, DefaultApi } from './gen'

const configuration: ConfigurationParameters = {
  basePath: API_URL,
  // fetchApi: safeFetch,
  headers: {
    'app-version': Package.version,
  },
  credentials: 'include',
}
console.log('DefaultApi', DefaultApi)
export const api = new DefaultApi(new Configuration(configuration))
