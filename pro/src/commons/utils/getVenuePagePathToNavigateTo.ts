export const getVenuePagePathToNavigateTo = (
  offererId: string | number,
  venueId: string | number,
  subPath: '' | '/edition' | '/parametres' = ''
) => {
  const basePath = `/structures/${offererId}/lieux/${venueId}`
  const context = location.pathname.includes('collectif')
    ? '/collectif'
    : location.pathname.includes('page-partenaire')
      ? '/page-partenaire'
      : ''

  return `${basePath}${context}${subPath}`
}
