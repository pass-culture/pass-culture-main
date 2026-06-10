import useSWR from 'swr/immutable'

import { apiNew } from '@/apiClient/api'
import { GET_EDUCATIONAL_DOMAINS_QUERY_KEY } from '@/commons/config/swrQueryKeys'

export const useEducationalDomains = () => {
  const result = useSWR(GET_EDUCATIONAL_DOMAINS_QUERY_KEY, () =>
    apiNew.listEducationalDomains()
  )
  return { ...result, data: result.data ?? [] }
}
