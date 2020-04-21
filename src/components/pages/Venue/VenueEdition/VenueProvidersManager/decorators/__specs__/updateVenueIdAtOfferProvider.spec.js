import { handleUpdateOnProviderField } from '../updateVenueIdAtOfferProvider'

describe('src | components | pages | Venue | VenueProvidersManager | decorators', () => {
  it('should not update venueIdAtOfferProvider value when provider identifier is required', () => {
    // given
    const inputValue = '{"requireProviderIdentifier": true}'
    const inputName = 'provider'
    const formValues = {
      siret: '12345',
    }

    // when
    const result = handleUpdateOnProviderField(inputValue, inputName, formValues)

    // then
    expect(result).toStrictEqual({
      venueIdAtOfferProvider: '',
    })
  })

  it('should update venueIdAtOfferProvider value using siret when provider identifier is not required', () => {
    // given
    const inputValue = '{"requireProviderIdentifier": false}'
    const inputName = 'provider'
    const formValues = {
      siret: '12345',
    }

    // when
    const result = handleUpdateOnProviderField(inputValue, inputName, formValues)

    // then
    expect(result).toStrictEqual({
      venueIdAtOfferProvider: '12345',
    })
  })
})
