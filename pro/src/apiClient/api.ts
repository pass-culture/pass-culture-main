import { API_URL } from 'utils/config'

import { AppClient, OpenAPIConfig } from './v1'
import { AppClientV2 } from './v2'

const config: OpenAPIConfig = {
  BASE: API_URL,
  VERSION: '1',
  WITH_CREDENTIALS: true,
  CREDENTIALS: 'include',
}

export const api = new AppClient(config).default
export const apiContremarque = new AppClientV2(config).apiContremarque
export const apiStocks = new AppClientV2(config).apiStocks
export { apiEntreprise, ENTREPRISE_STATUS_ACTIVE } from 'apiClient/entreprise'
