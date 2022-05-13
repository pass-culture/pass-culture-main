import { APIConfiguration, APIContremarqueApi, APIStocksApi } from './gen'

import { API_URL } from 'utils/config'

const configuration: APIConfiguration = {
  basePath: API_URL,
}

export const apiStock = new APIStocksApi(configuration)
export const apiContremarque = new APIContremarqueApi(configuration)
