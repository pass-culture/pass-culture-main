export const getVenuePagePathToNavigateTo = (
  subPath: '' | '/edition' | '/parametres' = ''
) => {
  const cleanPathname = location.pathname.replace(/\/(edition|parametres)$/, '')

  const pathName =
    cleanPathname.includes('page-partenaire') ||
    cleanPathname.includes('page-collective')
      ? cleanPathname
      : '/partenaire/page-individuelle'

  return `${pathName}${subPath}`
}
