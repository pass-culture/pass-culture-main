import { ApiError } from './v1'

export const serializeApiErrors = (
  errors: Record<string, string>,
  apiFieldsMap: Record<string, string> = {}
): Record<string, string> => {
  Object.entries(apiFieldsMap).forEach(([key, value]) => {
    if (errors[key]) {
      errors[value] = errors[key]
      delete errors[key]
    }
  })
  return errors
}

// defaultMessage = 'Une erreur s’est produite, veuillez réessayer'

export const getErrorCode = (error: ApiError): string => {
  return error.body.code
}

export const isError = (error: unknown): error is Error =>
  typeof error === 'object' && error !== null && 'message' in error

export const isErrorAPIError = (error: unknown): error is ApiError =>
  isError(error) && 'name' in error && error.name === 'ApiError'

export const getError = (error: ApiError): any => {
  return error.body
}

export const getHumanReadableApiError = (errors: any) => {
  if (errors instanceof Array) {
    return errors
      .map((error) =>
        Object.keys(error)
          .map((key) => error[key])
          .join(' ')
      )
      .join(' ')
  }

  if (errors instanceof Object) {
    return Object.keys(errors)
      .map((key) => errors[key].map((error: any) => error).join(' '))
      .join(' ')
  }

  return ''
}

// FIXME: find a way to test this by mocking ReadableStream
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
