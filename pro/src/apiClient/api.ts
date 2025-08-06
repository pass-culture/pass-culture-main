import { API_URL } from '@/commons/utils/config'

import { AppClientAdage } from './adage/AppClientAdage'
import { AppClient, OpenAPIConfig } from './v1'

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
export const apiAdage = new AppClientAdage(configAdage).default

export {
  getDataFromAddress,
  getDataFromAddressParts,
} from '@/apiClient/adresse/apiAdresse'
