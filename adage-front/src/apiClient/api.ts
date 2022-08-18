import { API_URL } from 'utils/config'

import { AppClient } from './AppClient'
import { OpenAPIConfig } from './core/OpenAPI'

const params = new URLSearchParams(window.location.search)
const token = params.get('token')

const config: OpenAPIConfig = {
  BASE: API_URL,
  VERSION: '1',
  WITH_CREDENTIALS: false,
  CREDENTIALS: 'omit',
  TOKEN: token ?? '',
}

export const api = new AppClient(config).default
