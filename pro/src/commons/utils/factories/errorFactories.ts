import { ApiError } from '@/apiClient/v1/core/ApiError'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'

interface ApiErrorFactoryOptions {
  status?: number
  statusText?: string
  body?: Record<string, unknown>
  message?: string
  method?: string
  url?: string
}

export const makeApiError = ({
  status = 400,
  statusText = 'Bad Request',
  body = {},
  message = '',
  method = 'GET',
  url = '',
}: ApiErrorFactoryOptions = {}): ApiError =>
  new ApiError(
    { method, url } as ApiRequestOptions,
    { ok: false, status, statusText, body, url } as ApiResult,
    message
  )
