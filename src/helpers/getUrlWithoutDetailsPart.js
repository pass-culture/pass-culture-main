import isDetailsView from './isDetailsView'

const getUrlWithoutDetailsPart = (location, match) => {
  const areDetails = isDetailsView(match)
  const { pathname, search } = location

  if (areDetails) {
    return `${pathname.split('/details')[0]}${search}`
  }
}

export default getUrlWithoutDetailsPart
