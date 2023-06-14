import { API_URL } from 'utils/config'

import { AppClientAdage } from './adage/AppClientAdage'
import { AppClient, OpenAPIConfig } from './v1'
import { AppClientV2 } from './v2'

const params = new URLSearchParams(window.location.search)
const token = params.get('token')

const config: OpenAPIConfig = {
  BASE: API_URL,
  VERSION: '1',
  WITH_CREDENTIALS: true,
  CREDENTIALS: 'include',
}

const configAdage: OpenAPIConfig = {
  BASE: API_URL,
  VERSION: '1',
  WITH_CREDENTIALS: false,
  CREDENTIALS: 'omit',
  TOKEN: token ?? '',
}

export const api = new AppClient(config).default
export const apiContremarque = new AppClientV2(config).apiContremarque
export const apiAdage = new AppClientAdage(configAdage).default
export { apiAdresse } from 'apiClient/adresse'
