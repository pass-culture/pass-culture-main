type ErrorWithErrorsCode = {
  status: number
  errors: {
    code: string
  }
}

export const hasStatusCodeAndErrorsCode = (
  // biome-ignore lint/suspicious/noExplicitAny: Generic error type.
  error: any
): error is ErrorWithErrorsCode =>
  typeof error?.status === 'number' && typeof error?.errors?.code === 'string'
