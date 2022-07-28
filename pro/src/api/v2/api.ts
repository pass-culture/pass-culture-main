import { API_URL } from 'utils/config'

import { APIConfiguration, APIStocksApi } from './gen'

const configuration: APIConfiguration = {
  basePath: API_URL,
}

export const apiStock = new APIStocksApi(configuration)
