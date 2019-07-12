import createDecorator from 'final-form-calculate'

export const handleUpdateOnProviderField = (inputValue, inputName, formValues) => {
  const parsedValue = JSON.parse(inputValue)
  const siret = !parsedValue.requireProviderIdentifier ? formValues.siret : ''

  return {
    venueIdAtOfferProvider: siret,
  }
}

const updateVenueIdAtOfferProvider = createDecorator({
  field: 'provider',
  updates: handleUpdateOnProviderField,
})

export default updateVenueIdAtOfferProvider
