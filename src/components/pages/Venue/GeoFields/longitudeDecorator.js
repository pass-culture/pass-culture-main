import createDecorator from 'final-form-calculate'

import getGeoSuggestionsFromLatitudeAndLongitude from './getGeoSuggestionsFromLatitudeAndLongitude'

export const longitudeDecorator = createDecorator({
  field: 'longitude',
  updates: async (longitude, key, values) => {
    const latitude = values.latitude
    if (!latitude || !longitude) {
      return {}
    }
    const result = await getGeoSuggestionsFromLatitudeAndLongitude(
      latitude,
      longitude
    )

    if (result.error) {
      return {}
    }

    if (result.data.length === 0 || result.data.length > 1) {
      return {
        address: null,
        city: null,
        latitude,
        longitude,
        postalCode: null,
        selectedAddress: null,
      }
    }

    const { address, city, postalCode } = result.data[0]
    return {
      address,
      city,
      latitude,
      longitude,
      postalCode,
      selectedAddress: null,
    }
  },
})

export default longitudeDecorator
