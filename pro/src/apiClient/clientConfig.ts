import { logout } from '@/commons/store/user/dispatchers/logout'
import { API_URL, URL_FOR_MAINTENANCE } from '@/commons/utils/config'

import type { CreateClientConfig } from './v1/new/client.gen'

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

    if (
      !url.includes('/users/current') &&
      !url.includes('/offerers/names') &&
      !url.includes('/users/signin')
    ) {
      await logout()
      return new Promise<Response>(() => {})
    }
  }

  return response
}

export const createClientConfig: CreateClientConfig = (config) => ({
  ...config,
  baseUrl: API_URL,
  credentials: 'include',
  throwOnError: true,
  responseStyle: 'data',
  fetch: customFetch,
})
