import { AppClientAdage } from '@/apiClient/adage'
import { ApiError } from '@/apiClient/compat'
import { API_URL } from '@/commons/utils/config'

import { client as adageClient } from './adage/new/client.gen'
import { AppClient, type OpenAPIConfig } from './v1'
import { client as v1Client } from './v1/new/client.gen'

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

function createApiErrorInterceptor() {
  return async (
    error: unknown,
    response: Response | undefined,
    request: Request
  ) =>
    new ApiError(
      request.url,
      response?.status ?? 0,
      response?.statusText ?? '',
      error
    )
}

v1Client.interceptors.error.use(createApiErrorInterceptor())
adageClient.interceptors.error.use(createApiErrorInterceptor())

export const api = new AppClient(config).default
export const apiAdage = new AppClientAdage(configAdage).default

export * as apiAdageNew from '@/apiClient/adage/new/sdk.gen'
export {
  getDataFromAddress,
  getDataFromAddressParts,
} from '@/apiClient/adresse/apiAdresse'
export * as apiNew from '@/apiClient/v1/new/sdk.gen'
