export const queryParamsFromOfferer = location => {
  const queryParams = new URLSearchParams(location.search)
  const hasOfferer = queryParams.has('structure')
  const hasVenue = queryParams.has('lieu')

  return {
    structure: hasOfferer ? queryParams.get('structure') : '',
    lieu: hasVenue ? queryParams.get('lieu') : '',
  }
}
