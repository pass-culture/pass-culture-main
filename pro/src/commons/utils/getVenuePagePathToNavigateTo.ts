export const getVenuePagePathToNavigateTo = (subPath: '' | '/edition' = '') => {
  const cleanPathname = location.pathname.replace(/\/(edition)$/, '')

  const pathName = /page-(partenaire|collective)/.test(cleanPathname)
    ? cleanPathname
    : '/partenaire/page-partenaire'

  return `${pathName}${subPath}`
}
