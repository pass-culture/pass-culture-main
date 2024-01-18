import { GetOffererResponseModel } from 'apiClient/v1'

import { transformOffererResponseModelToOfferer } from '../Offerer'

describe('transformOffererResponseModelToOfferer', () => {
  it('should instantiate Offerer object with offerer values', () => {
    // Given
    const properties: GetOffererResponseModel = {
      id: 5,
      name: 'Offerer 3',
      postalCode: '75001',
      city: 'PARIS',
      dateCreated: '2020-01-01T00:00:00.000Z',
      apiKey: {
        maxAllowed: 100,
        prefixes: [],
      },
      hasAvailablePricingPoints: true,
      hasDigitalVenueAtLeastOneOffer: true,
      hasValidBankAccount: true,
      hasPendingBankAccount: false,
      hasNonFreeOffer: true,
      hasActiveOffer: true,
      venuesWithNonFreeOffersWithoutBankAccounts: [],
      isValidated: true,
      isActive: true,
    }

    expect(transformOffererResponseModelToOfferer(properties)).toMatchObject({
      id: 5,
      postalCode: '75001',
      city: 'PARIS',
    })
  })
})
