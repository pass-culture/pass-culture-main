import {
  ApiError,
  type ApiRequestOptions,
  type ApiResult,
} from '@/apiClient/compat'

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
