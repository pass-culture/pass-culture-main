import createDecorator from 'final-form-calculate'

import getGeoSuggestionsFromLatitudeAndLongitude from './getGeoSuggestionsFromLatitudeAndLongitude'

export const longitudeDecorator = createDecorator({
  field: 'longitude',
  updates: async (longitude, key, values) => {
    if (!values.latitude || !longitude || values.address || values.siret) {
      return {}
    }

    const result = await getGeoSuggestionsFromLatitudeAndLongitude(
      values.latitude,
      longitude
    )

    if (result.error) {
      return {}
    }

    const hasSingleClearResult = result.data && result.data.length === 1
    if (hasSingleClearResult) {
      const { address, city, postalCode } = result.data[0]
      return {
        address,
        city,
        postalCode,
        selectedAddress: null,
      }
    }

    return {
      address: null,
      city: null,
      postalCode: null,
      selectedAddress: null,
    }
  },
})

export default longitudeDecorator
