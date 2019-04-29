import createDecorator from 'final-form-calculate'

import getGeoSuggestionsFromLatitudeAndLongitude from './getGeoSuggestionsFromLatitudeAndLongitude'

export const latitudeDecorator = createDecorator({
  field: 'latitude',
  updates: async (latitude, key, values) => {
    const longitude = values.longitude
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

export default latitudeDecorator
