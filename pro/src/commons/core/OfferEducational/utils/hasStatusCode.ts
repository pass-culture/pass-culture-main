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
