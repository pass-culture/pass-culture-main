/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import type { GetOffererAddressResponseModel } from '@/apiClient/v1'

let offererAddressId = 1

export const offererAddressFactory = (
  customOffererAddress: Partial<GetOffererAddressResponseModel> = {}
): GetOffererAddressResponseModel => {
  const currentOaId = offererAddressId++

  return {
    id: currentOaId,
    label: null,
    street: '1 Rue de paris',
    city: 'Paris',
    postalCode: '75001',
    departmentCode: '75',
    ...customOffererAddress,
  }
}
