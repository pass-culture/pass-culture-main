import createDecorator from 'final-form-calculate'

import getSuggestionsFromLatitudeAndLongitude from '../selectors/getSuggestionsFromLatitudeAndLongitude'

const bindGetSuggestionsToLongitude = createDecorator({
  field: 'longitude',
  updates: async (longitude, key, values) => {
    if (!values.latitude || !longitude || values.address || values.siret) {
      return {}
    }

    const result = await getSuggestionsFromLatitudeAndLongitude(
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
        isLocationFrozen: false,
        postalCode,
      }
    }

    return {
      address: null,
      city: null,
      isLocationFrozen: false,
      postalCode: null,
    }
  },
})

export default bindGetSuggestionsToLongitude
