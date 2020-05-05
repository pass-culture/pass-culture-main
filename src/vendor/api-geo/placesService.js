import typeEnum from './typeEnum'

const API_ADRESSE_URL = `https://api-adresse.data.gouv.fr/search`

export const fetchPlaces = ({ keywords, limit = 20 }) => {
  return fetch(`${API_ADRESSE_URL}/?limit=${limit}&q=${keywords}`)
    .then(response => response.json())
    .then(suggestedPlaces => {
      return suggestedPlaces.features.map(feature => {
        const { geometry: { coordinates }, properties } = feature
        const { city, context, name, type } = properties
        const contextWithoutSpaces = context.replace(/\s+/g, '')
        const splittedInformation = contextWithoutSpaces.split(',')
        const { STREET, HOUSE_NUMBER } = typeEnum

        return {
          name: {
            long: type === STREET || type === HOUSE_NUMBER ? `${name}, ${city}` : city,
            short: type === STREET || type === HOUSE_NUMBER ? name : city
          },
          extraData: {
            city: city,
            department: splittedInformation[1] || '',
          },
          geolocation: {
            longitude: coordinates[0] || '',
            latitude: coordinates[1] || '',
          },
        }
      })
    })
    .catch(() => {
      return []
    })
}
