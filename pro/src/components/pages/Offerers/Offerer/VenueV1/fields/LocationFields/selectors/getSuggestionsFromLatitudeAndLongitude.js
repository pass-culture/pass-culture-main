import createCachedSelector from 're-reselect'

import fetchAddressData from '../utils/fetchAddressData'

function mapArgsToCacheKey(latitude, longitude, maxSuggestions) {
  return `${latitude || ''}/${longitude || ''}/${maxSuggestions || ''}`
}

const getSuggestionsFromLatitudeAndLongitude = createCachedSelector(
  latitude => latitude,
  (latitude, longitude) => longitude,
  async (latitude, longitude) => {
    const addressUrl = `https://api-adresse.data.gouv.fr/reverse/?lat=${latitude}&lon=${longitude}`
    try {
      const data = await fetchAddressData(addressUrl)
      return { data }
    } catch (e) {
      const error = 'Impossible de vérifier les latitude et longitude saisies.'
      return { error }
    }
  }
)(mapArgsToCacheKey)

export default getSuggestionsFromLatitudeAndLongitude
