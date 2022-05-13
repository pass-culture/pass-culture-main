import { APIConfiguration, DefaultApi } from './gen'

import { API_URL } from 'utils/config'

const configuration: APIConfiguration = {
  basePath: API_URL,
}

export const api = new DefaultApi(configuration)
