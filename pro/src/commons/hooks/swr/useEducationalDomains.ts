import { api } from 'apiClient/api'
import { GET_EDUCATIONAL_DOMAINS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import useSWR from 'swr'

export const useEducationalDomains = () => {
  return useSWR(
    GET_EDUCATIONAL_DOMAINS_QUERY_KEY,
    () => api.listEducationalDomains(),
    { fallbackData: [] }
  )
}
