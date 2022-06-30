import { ApiError } from './v1'

export const getErrorCode = (error: ApiError): string => {
  return error.body.code
}

export const isErrorAPIError = (error: any): error is ApiError =>
  'name' in error && error.name === 'ApiError'
