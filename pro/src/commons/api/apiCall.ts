import { FrontendError } from '@/commons/errors/FrontendError'

export async function apiCall<T>(promise: Promise<T | undefined>): Promise<T> {
  const result = await promise
  if (result === undefined) {
    throw new FrontendError(
      'API call returned undefined despite throwOnError: true. This should never happen.'
    )
  }
  return result
}
