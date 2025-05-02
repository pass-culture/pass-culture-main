import type { Location } from 'react-router'

export const queryParamsFromOfferer = (location: Location) => {
  const queryParams = new URLSearchParams(location.search)
  const hasVenue = queryParams.has('lieu')
  const hasRequest = queryParams.has('requete')

  return {
    lieu: hasVenue ? queryParams.get('lieu') : '',
    requete: hasRequest ? queryParams.get('requete') : '',
  }
}
