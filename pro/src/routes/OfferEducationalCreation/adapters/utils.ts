// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types
export const hasStatusCode = (error: any): error is { status: number } =>
  typeof error.status === 'number'
