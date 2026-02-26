import useSWR from 'swr/immutable'

import { api } from '@/apiClient/api'
import { GET_EDUCATIONAL_DOMAINS_QUERY_KEY } from '@/commons/config/swrQueryKeys'

export const useEducationalDomains = () => {
  const result = useSWR(GET_EDUCATIONAL_DOMAINS_QUERY_KEY, () =>
    api.listEducationalDomains()
  )
  return { ...result, data: result.data ?? [] }
}
