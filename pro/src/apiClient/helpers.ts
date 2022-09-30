import { ApiError } from './v1'

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
export const getDataURLFromImageURL = async (
  imageURL: string
): Promise<File> => {
  const response = await fetch(imageURL)
  const blob = await response.blob()
  return new File([blob], 'image.jpg', { type: blob.type })
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
