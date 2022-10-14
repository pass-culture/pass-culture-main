import { ApiError } from './v1'

export const serializeApiErrors = (
  apiFieldsMap: Record<string, string>,
  errors: Record<string, string>
): Record<string, string> => {
  const formErrors: Record<string, string> = {}
  let formFieldName
  for (const apiFieldName in errors) {
    formFieldName =
      apiFieldName in apiFieldsMap ? apiFieldsMap[apiFieldName] : apiFieldName
    formErrors[formFieldName] = errors[apiFieldName]
  }
  return formErrors
}

export const getErrorCode = (error: ApiError): string => {
  return error.body.code
}

export const isErrorAPIError = (error: any): error is ApiError =>
  'name' in error && error.name === 'ApiError'

export const getError = (error: ApiError): any => {
  return error.body
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
