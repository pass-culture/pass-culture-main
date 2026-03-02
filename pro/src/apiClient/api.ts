import { API_URL } from '@/commons/utils/config'

import { AppClientAdage } from './adage/AppClientAdage'
import { client as adageClient } from './adage/new/client.gen'
import * as adageSdk from './adage/new/sdk.gen'
import { ApiError } from './compat'
import { AppClient, type OpenAPIConfig } from './v1'
import { client as v1Client } from './v1/new/client.gen'
import * as v1Sdk from './v1/new/sdk.gen'

const params = new URLSearchParams(window.location.search)
const token = params.get('token')

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

export const apiNew = v1Sdk
export const apiAdageNew = adageSdk

export {
  getDataFromAddress,
  getDataFromAddressParts,
} from '@/apiClient/adresse/apiAdresse'
