/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import { GetOffererAddressWithIsEditableResponseModel } from 'apiClient/v1'

let offererAddressId = 1

export const offererAddressFactory = (
  customOffererAddress: Partial<GetOffererAddressWithIsEditableResponseModel> = {}
): GetOffererAddressWithIsEditableResponseModel => {
  const currentOaId = offererAddressId++

  return {
    id: currentOaId,
    city: 'Paris',
    isEditable: true,
    postalCode: '75001',
    street: '1 Rue de paris',
    ...customOffererAddress,
  }
}
