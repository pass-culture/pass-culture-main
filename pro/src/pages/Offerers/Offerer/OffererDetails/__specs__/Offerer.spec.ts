import { GetOffererResponseModel } from 'apiClient/v1'

import { transformOffererResponseModelToOfferer } from '../Offerer'

describe('transformOffererResponseModelToOfferer', () => {
  it('should instantiate Offerer object with offerer values', () => {
    // Given
    const properties: GetOffererResponseModel = {
      nonHumanizedId: 5,
      name: 'Offerer 3',
      postalCode: '75001',
      city: 'PARIS',
      dateCreated: '2020-01-01T00:00:00.000Z',
      fieldsUpdated: ['postalCode', 'city'],
      apiKey: {
        maxAllowed: 100,
        prefixes: [],
      },
      hasAvailablePricingPoints: true,
      hasDigitalVenueAtLeastOneOffer: true,
      isValidated: true,
      isActive: true,
    }

    expect(transformOffererResponseModelToOfferer(properties)).toMatchObject({
      nonHumanizedId: 5,
      postalCode: '75001',
      city: 'PARIS',
    })
  })
})
