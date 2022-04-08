import Package from '../../../../package.json'
import { API_URL } from 'utils/config'

import { APIConfiguration, APIConfigurationParameters, DefaultApi } from './gen'

const configuration: APIConfigurationParameters = {
  basePath: API_URL,
  // fetchApi: safeFetch,
  headers: {
    'app-version': Package.version,
  },
  credentials: 'include',
}

export const api = new DefaultApi(new APIConfiguration(configuration))
