export const getPathToNavigateTo = (
  offererId: string | number,
  venueId: string | number,
  isEdition = false
) => {
  const basePath = `/structures/${offererId}/lieux/${venueId}`
  const context = location.pathname.includes('collectif')
    ? '/collectif'
    : location.pathname.includes('page-partenaire')
      ? '/page-partenaire'
      : ''

  return `${basePath}${context}${isEdition ? '/edition' : ''}`
}
