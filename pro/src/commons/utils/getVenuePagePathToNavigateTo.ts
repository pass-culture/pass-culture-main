export const getVenuePagePathToNavigateTo = (
  subPath: '' | '/edition' | '/parametres' = ''
) => {
  const pathName =
    location.pathname.includes('page-partenaire') ||
    location.pathname.includes('page-collective')
      ? location.pathname
      : '/partenaire/page-individuelle'

  return `${pathName}${subPath}`
}
