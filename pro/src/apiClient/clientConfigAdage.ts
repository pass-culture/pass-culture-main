import { API_URL, URL_FOR_MAINTENANCE } from '@/commons/utils/config'

import type { CreateClientConfig } from './adage/client.gen'

const params = new URLSearchParams(window.location.search)
const token = params.get('token')

const customFetch: typeof fetch = async (input, init) => {
  const response = await fetch(input, init)

  if (response.status === 503) {
    window.location.assign(URL_FOR_MAINTENANCE)
    return new Promise<Response>(() => {})
  }

  if (response.status === 401) {
    const url =
      typeof input === 'string'
        ? input
        : input instanceof URL
          ? input.href
          : input.url

    if (url.includes('/adage-iframe')) {
      window.location.href = '/adage-iframe/erreur'
      return new Promise<Response>(() => {})
    }
  }

  return response
}

export const createClientConfig: CreateClientConfig = (config) => ({
  ...config,
  baseUrl: API_URL,
  credentials: 'omit',
  throwOnError: true,
  responseStyle: 'data',
  fetch: customFetch,
  headers: {
    Authorization: token ? `Bearer ${token}` : '',
  },
})
