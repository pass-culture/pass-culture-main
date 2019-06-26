import createDecorator from 'final-form-calculate'

export const handleUpdateOnProviderField = () => {
  return (inputValue, inputName, formValues) => {
    const parsedValue = JSON.parse(inputValue)

    if (!parsedValue.requireProviderIdentifier) {
      return {
        ['venueIdAtOfferProvider']: formValues.siret
      }
    }
    return {
      ['venueIdAtOfferProvider']: ''
    }
  }
}

const updateVenueIdAtOfferProvider = createDecorator(
  {
    field: 'provider',
    updates: handleUpdateOnProviderField()
  })

export default updateVenueIdAtOfferProvider
