const API_ADRESSE_URL = `https://api-adresse.data.gouv.fr/search`

export const fetchPlaces = ({ keywords, limit = 10 }) => {
  return fetch(`${API_ADRESSE_URL}/?limit=${limit}&q=${keywords}`)
    .then(response => response.json())
    .then(suggestedPlaces => {
      return suggestedPlaces.features.map(feature => {
        const { geometry: { coordinates }, properties } = feature
        const { city, context, label } = properties
        const contextWithoutSpaces = context.replace(/\s+/g, '')
        const splittedInformation = contextWithoutSpaces.split(',')

        return {
          extraData: {
            departmentCode: splittedInformation[0] || '',
            department: splittedInformation[1] || '',
            label: label,
            region: splittedInformation[2] || ''
          },
          geolocation: {
            latitude: coordinates[0] || '',
            longitude: coordinates[1] || '',
          },
          name: city,
        }
      })
    })
    .catch(() => {
      return []
    })
}
