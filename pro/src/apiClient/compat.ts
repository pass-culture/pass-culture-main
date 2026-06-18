type OnCancel = (handler: () => void) => void

export type ApiRequestOptions = {
  readonly method:
    | 'GET'
    | 'PUT'
    | 'POST'
    | 'DELETE'
    | 'OPTIONS'
    | 'HEAD'
    | 'PATCH'
  readonly url: string
  readonly path?: Record<string, unknown>
  readonly cookies?: Record<string, unknown>
  readonly headers?: Record<string, unknown>
  readonly query?: Record<string, unknown>
  readonly formData?: Record<string, unknown>
  readonly body?: unknown
  readonly mediaType?: string
  readonly responseHeader?: string
  readonly errors?: Record<number, string>
}

export type ApiResult = {
  readonly url: string
  readonly ok: boolean
  readonly status: number
  readonly statusText: string
  readonly body: unknown
}

export class ApiError extends Error {
  public readonly url: string
  public readonly status: number
  public readonly statusText: string
  // biome-ignore lint/suspicious/noExplicitAny: matches original openapi-typescript-codegen signature
  public readonly body: Record<string, any>
  public readonly originalError: unknown

  constructor(request: ApiRequestOptions, response: ApiResult, message: string)
  constructor(
    url: string,
    status: number,
    statusText: string,
    originalError: unknown
  )
  constructor(
    urlOrRequest: string | ApiRequestOptions,
    statusOrResponse: number | ApiResult,
    statusTextOrMessage: string,
    originalError?: unknown
  ) {
    if (typeof urlOrRequest === 'string') {
      super(`${statusOrResponse} ${statusTextOrMessage}`)
      this.url = urlOrRequest
      this.status = statusOrResponse as number
      this.statusText = statusTextOrMessage
      this.body =
        typeof originalError === 'object' && originalError !== null
          ? originalError
          : {}
      this.originalError = originalError
    } else {
      const response = statusOrResponse as ApiResult
      super(statusTextOrMessage)
      this.url = response.url
      this.status = response.status
      this.statusText = response.statusText
      this.body =
        typeof response.body === 'object' && response.body !== null
          ? response.body
          : {}
    }
    this.name = 'ApiError'
  }
}

export class CancelError extends Error {
  constructor(message = 'CancelError') {
    super(message)
    this.name = 'CancelError'
  }
}

export class CancelablePromise<T> extends Promise<T> {
  static get [Symbol.species]() {
    return Promise
  }

  constructor(
    executor: (
      resolve: (value: T | PromiseLike<T>) => void,
      reject: (reason?: unknown) => void,
      onCancel?: OnCancel
    ) => void
  ) {
    super((resolve, reject) => executor(resolve, reject, () => null))
  }

  cancel() {
    return
  }
}
