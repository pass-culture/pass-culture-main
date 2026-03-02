import type { FieldValues, Path, UseFormSetError } from 'react-hook-form'

import type { ApiError } from './v1'

export function serializeApiErrors<T extends FieldValues>(
  errors: Record<string, string[]>,
  setError: UseFormSetError<T>
) {
  Object.entries(errors).forEach(([key, value]) => {
    setError(key as Path<T>, { type: 'custom', message: value.join(' ') })
  })
}

type ErrorAdage = {
  statusCode: number
  body: {
    code: string
  }
}

// TODO remove this function because it is use at only one place
// biome-ignore lint/suspicious/noExplicitAny: Generic error.
export const hasErrorCode = (error: any): error is ErrorAdage =>
  typeof error?.body?.code === 'string'

export const getErrorCode = (error: ApiError): string => {
  return error.body.code
}

export const isError = (error: unknown): error is Error =>
  typeof error === 'object' && error !== null && 'message' in error

export const isErrorAPIError = (error: unknown): error is ApiError =>
  isError(error) && 'name' in error && error.name === 'ApiError'

export const getError = (error: ApiError) => {
  return error.body
}

export const getHumanReadableApiError = (
  error: unknown,
  defaultMessage = 'Une erreur s’est produite, veuillez réessayer'
) => {
  if (!isErrorAPIError(error)) {
    return defaultMessage
  }

  const { body } = error

  if (Array.isArray(body) && body.length > 0) {
    return body.map((bodyValue) => Object.values(bodyValue).join(' ')).join(' ')
  }

  if (body instanceof Object && Object.keys(body).length > 0) {
    return Object.values(body)
      .map((bodyValue) =>
        Array.isArray(bodyValue) ? bodyValue.join(' ') : bodyValue
      )
      .join(' ')
  }

  return defaultMessage
}

// TODO: find a way to test this by mocking ReadableStream
// in fetch response
/* istanbul ignore next */
export const getFileFromURL = async (
  url: string,
  name = 'image.jpg'
): Promise<File> => {
  const response = await fetch(url)
  const blob = await response.blob()
  return new File([blob], name, { type: blob.type })
}

export const HTTP_STATUS = {
  NO_CONTENT: 204,
  FORBIDDEN: 403,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
  TOO_MANY_REQUESTS: 429,
  GONE: 410,
  NOT_FOUND: 404,
}
