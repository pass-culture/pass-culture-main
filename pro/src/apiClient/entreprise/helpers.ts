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

export function isApiError(error: ApiError | unknown): error is ApiError {
  return (error as ApiError).name === 'ApiError'
}
