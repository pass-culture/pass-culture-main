import createDecorator from 'final-form-calculate'

import getGeoSuggestionsFromLatitudeAndLongitude from './getGeoSuggestionsFromLatitudeAndLongitude'

export const latitudeDecorator = createDecorator({
  field: 'latitude',
  updates: async (latitude, key, values) => {
    if (!latitude || !values.longitude || values.address || values.siret) {
      return {}
    }

    const result = await getGeoSuggestionsFromLatitudeAndLongitude(
      latitude,
      values.longitude
    )

    if (result.error) {
      return {}
    }

    if (result.data.length !== 1) {
      return {
        address: null,
        city: null,
        postalCode: null,
        selectedAddress: null,
      }
    }

    const { address, city, postalCode } = result.data[0]
    return {
      address,
      city,
      postalCode,
      selectedAddress: null,
    }
  },
})

export default latitudeDecorator
