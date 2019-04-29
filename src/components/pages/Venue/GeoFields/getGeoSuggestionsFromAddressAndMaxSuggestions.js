import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(address, maxSuggestions) {
  return `${address || ''}/${maxSuggestions || ''}`
}

const getGeoSuggestionsFromAddressAndMaxSuggestions = createCachedSelector(
  address => address,
  (address, maxSuggestions) => maxSuggestions,
  async (address, maxSuggestions) => {
    const wordsCount = address.split(/\s/).filter(v => v).length
    if (wordsCount < 2)
      return {
        data: [],
      }

    const addressUrl = `https://api-adresse.data.gouv.fr/search/?limit=${maxSuggestions}&q=${address}`

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
      const error = "Impossible de vérifier l'adresse saisie."
      return { error }
    }
  }
)(mapArgsToCacheKey)

export default getGeoSuggestionsFromAddressAndMaxSuggestions
