import { API_URL } from 'utils/config'

import { APIConfiguration, DefaultApi } from './gen'

const configuration: APIConfiguration = {
  basePath: API_URL,
}

export const api = new DefaultApi(configuration)
