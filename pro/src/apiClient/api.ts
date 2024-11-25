import * as generatedAdageApi from 'apiClient/adage/api'
import { OpenAPIConfig } from 'apiClient/core/OpenAPI'
import * as generatedV1Api from 'apiClient/v1/api'
import * as generatedV2Api from 'apiClient/v2/api'
import { API_URL } from 'utils/config'

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

export const api = new generatedV1Api.DefaultApi(config)
export const apiContremarque = new generatedV2Api.DprcieAPIContremarqueApi(
  config
)
export const apiAdage = new generatedAdageApi.DefaultApi(configAdage)
export { apiAdresse } from 'apiClient/adresse/apiAdresse'
