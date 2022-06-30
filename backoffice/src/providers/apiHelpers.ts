import { fetchUtils, HttpError } from 'react-admin'

export class PcApiHttpError extends HttpError {
  readonly message!: string
  readonly status!: number
  readonly body!: string
}

export async function safeFetch(url: string, options: RequestInit = {}) {
  if (!options.headers) {
    options.headers = new Headers({ Accept: 'application/json' })
  }
  const token = localStorage.getItem('tokenApi')
  if (token) {
    options.headers = new Headers({
      ...options.headers,
      Authorization: `Bearer ${token}`,
    })
  }

  return fetchUtils.fetchJson(url, options)
}

export function getHttpApiErrorMessage(error: PcApiHttpError) {
  return Object.values(error.body)[0]
}
