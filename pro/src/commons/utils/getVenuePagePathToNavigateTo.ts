export const getVenuePagePathToNavigateTo = (
  offererId: string | number,
  venueId: string | number,
  subPath: '' | '/edition' | '/parametres' = ''
) => {
  const basePath = `/structures/${offererId}/lieux/${venueId}`
  const isCollectif = location.pathname.includes('collectif')
  const whenIsPagePartenaire = location.pathname.includes('page-partenaire')
    ? '/page-partenaire'
    : ''
  const context = isCollectif ? '/collectif' : whenIsPagePartenaire

  return `${basePath}${context}${subPath}`
}
