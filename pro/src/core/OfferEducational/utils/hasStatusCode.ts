/* eslint-disable */
type Error = {
  status: number
  code: string
}

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

export const hasStatusCodeAndCode = (error: any): error is Error =>
  typeof error?.status === 'number' && typeof error?.code === 'string'
