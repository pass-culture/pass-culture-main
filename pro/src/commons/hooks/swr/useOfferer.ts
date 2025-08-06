import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GetOffererResponseModel } from '@/apiClient/v1'
import { GET_OFFERER_QUERY_KEY } from '@/commons/config/swrQueryKeys'

export const useOfferer = (
  selectedOffererId?: number | string | null,
  useFallbackData?: boolean
) => {
  const selectedOfferIdAsNumber =
    typeof selectedOffererId === 'string'
      ? Number(selectedOffererId)
      : selectedOffererId

  const { data, ...rest } = useSWR<
    GetOffererResponseModel | null,
    string,
    [string, number] | null
  >(
    selectedOfferIdAsNumber
      ? [GET_OFFERER_QUERY_KEY, selectedOfferIdAsNumber]
      : null,
    ([, offererIdParam]) => api.getOfferer(offererIdParam),
    {
      ...(useFallbackData ? { fallbackData: null } : {}),
      shouldRetryOnError: false,
      onError: () => {},
    }
  )

  return {
    data: data ?? null,
    ...rest,
  }
}
