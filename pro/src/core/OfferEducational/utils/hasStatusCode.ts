/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types */
type Error = {
  status: number
  code: string
}

export const hasStatusCode = (error: any): error is { status: number } =>
  typeof error.status === 'number'

export const hasStatusCodeAndCode = (error: any): error is Error =>
  typeof error.status === 'number' && typeof error.code === 'string'
