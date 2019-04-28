import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(latitude, longitude, maxSuggestions) {
  return `${latitude || ''}/${longitude || ''}/${maxSuggestions || ''}`
}

const getGeoSuggestionsFromLatitudeAndLongitude = createCachedSelector(
  latitude => latitude,
  (latitude, longitude) => longitude,
  async (latitude, longitude) => {
    const addressUrl = `https://api-adresse.data.gouv.fr/reverse/?lat=${latitude}&lon=${longitude}`

    try {
      const response = await fetch(addressUrl)

      if (response.status === 404) {
        const error = `Adresse invalide`
        return { error }
      }

      const json = await response.json()
      const data = json.features.map(f => ({
        address: f.properties.name,
        city: f.properties.city,
        id: f.properties.id,
        latitude: f.geometry.coordinates[1],
        longitude: f.geometry.coordinates[0],
        label: f.properties.label,
        postalCode: f.properties.postcode,
      }))

      return { data }
    } catch (e) {
      console.log('e', e)
      const error = 'Impossible de vérifier les latitude et longitude saisies.'
      return { error }
    }
  }
)(mapArgsToCacheKey)

export default getGeoSuggestionsFromLatitudeAndLongitude
