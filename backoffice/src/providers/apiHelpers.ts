import { fetchUtils, HttpError } from 'react-admin'

import { i18nProvider } from './i18nProvider'

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
      Authorization: `Bearer ${JSON.parse(token)}`,
    })
  }

  return fetchUtils.fetchJson(url, options)
}

export function getHttpApiErrorMessage(error: PcApiHttpError) {
  return Object.values(error.body)[0]
}

export const getErrorMessage = (message: string) => {
  const i18nContext = i18nProvider
  return i18nContext.translate(message, null)
}
