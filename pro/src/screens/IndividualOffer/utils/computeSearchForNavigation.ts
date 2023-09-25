export const computeSearchForNavigation = (locationSearch: string): string => {
  const queryParams = new URLSearchParams(locationSearch)
  const queryOffererId = queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')

  let search = ''

  if (queryOffererId && queryVenueId) {
    search = `structure=${queryOffererId}&lieu=${queryVenueId}`
  } else if (queryOffererId && !queryVenueId) {
    search = `structure=${queryOffererId}`
  }
  return search
}
