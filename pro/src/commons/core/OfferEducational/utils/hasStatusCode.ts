type ErrorWithErrorsCode = {
  status: number
  errors: {
    code: string
  }
}

export const hasStatusCodeAndErrorsCode = (
  error: any
): error is ErrorWithErrorsCode =>
  typeof error?.status === 'number' && typeof error?.errors?.code === 'string'

export const hasStatusCode = (error: any): error is { status: number } =>
  typeof error?.status === 'number'
