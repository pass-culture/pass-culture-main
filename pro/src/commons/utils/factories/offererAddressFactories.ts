/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import { GetOffererAddressResponseModel } from '@/apiClient/v1'

let offererAddressId = 1

export const offererAddressFactory = (
  customOffererAddress: Partial<GetOffererAddressResponseModel> = {}
): GetOffererAddressResponseModel => {
  const currentOaId = offererAddressId++

  return {
    id: currentOaId,
    city: 'Paris',
    isLinkedToVenue: true,
    postalCode: '75001',
    street: '1 Rue de paris',
    ...customOffererAddress,
  }
}
