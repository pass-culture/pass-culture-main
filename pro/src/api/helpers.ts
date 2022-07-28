export interface ApiErrorResonseMessages {
  global?: string[]
  [key: string]: string[] | undefined
}

export class ApiError extends Error {
  name = 'ApiError'
  content: any
  statusCode: number

  constructor(
    statusCode: number,
    content: ApiErrorResonseMessages,
    message?: string
  ) {
    super(message)
    this.content = content
    this.statusCode = statusCode
  }
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

export function isApiError(error: ApiError | unknown): error is ApiError {
  return (error as ApiError).name === 'ApiError'
}
