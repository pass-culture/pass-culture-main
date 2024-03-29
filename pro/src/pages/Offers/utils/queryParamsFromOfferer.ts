import type { Location } from 'react-router-dom'

export const queryParamsFromOfferer = (location: Location) => {
  const queryParams = new URLSearchParams(location.search)
  const hasOfferer = queryParams.has('structure')
  const hasVenue = queryParams.has('lieu')
  const hasRequest = queryParams.has('requete')

  return {
    structure: hasOfferer ? queryParams.get('structure') : '',
    lieu: hasVenue ? queryParams.get('lieu') : '',
    requete: hasRequest ? queryParams.get('requete') : '',
  }
}
