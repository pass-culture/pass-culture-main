import createDecorator from 'final-form-calculate'

import getSuggestionsFromLatitudeAndLongitude from '../selectors/getSuggestionsFromLatitudeAndLongitude'

const bindGetSuggestionsToLatitude = createDecorator({
  field: 'latitude',
  updates: async (latitude, key, values) => {
    console.log('process.env.NODE_ENV', process.env.NODE_ENV)
    if (
      !latitude ||
      !values.longitude ||
      values.siret ||
      process.env.NODE_ENV === 'test'
    ) {
      return {}
    }

    const result = await getSuggestionsFromLatitudeAndLongitude(
      latitude,
      values.longitude
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

export default bindGetSuggestionsToLatitude
