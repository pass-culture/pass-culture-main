import type { GetOffererResponseModel } from '@/apiClient//v1/models/GetOffererResponseModel'

/**
 * Returns offerer from store if id matches, otherwise fetches from API.
 * @param requestedOffererId - The offerer id requested
 * @param currentOfferer - The offerer object from the store
 * @param apiCall - Function to fetch offerer from API
 * @returns Promise<GetOffererResponseModel>
 */
export function getOffererData(
  requestedOffererId: number | null | undefined,
  currentOfferer: GetOffererResponseModel | null | undefined,
  apiCall: () => Promise<GetOffererResponseModel>
): Promise<GetOffererResponseModel | null> {
  if (
    requestedOffererId &&
    currentOfferer &&
    currentOfferer.id === requestedOffererId
  ) {
    return Promise.resolve(currentOfferer)
  }
  if (requestedOffererId === null) {
    return Promise.resolve(null)
  }
  return apiCall()
}
