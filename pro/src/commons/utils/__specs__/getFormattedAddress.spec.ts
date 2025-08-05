import { getAddressResponseIsLinkedToVenueModelFactory } from 'commons/utils/factories/commonOffersApiFactories'

import { getFormattedAddress } from '../getFormattedAddress'

const MOCK_ADDRESS = getAddressResponseIsLinkedToVenueModelFactory()

describe('getFormattedAddress', () => {
  it('should return formatted address with complete info', () => {
    const formattedAddress = getFormattedAddress(MOCK_ADDRESS)
    expect(formattedAddress).toBe(
      `${MOCK_ADDRESS.street}, ${MOCK_ADDRESS.postalCode} ${MOCK_ADDRESS.city}`
    )
  })

  it('should return formatted address without street', () => {
    const formattedAddress = getFormattedAddress({
      ...MOCK_ADDRESS,
      street: undefined,
    })
    expect(formattedAddress).toBe(
      `${MOCK_ADDRESS.postalCode} ${MOCK_ADDRESS.city}`
    )
  })
})
