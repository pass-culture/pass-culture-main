import { fetchUtils } from 'react-admin'

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
