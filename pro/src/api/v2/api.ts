import { API_URL } from 'utils/config'

import { APIConfiguration, APIStocksApi, APIContremarqueApi } from './gen'

const configuration: APIConfiguration = {
  basePath: API_URL,
}

export const apiStock = new APIStocksApi(configuration)
export const apiContremarque = new APIContremarqueApi(configuration)
