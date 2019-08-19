import areDetailsVisible from './areDetailsVisible'

const getUrlWithoutDetailsPart = (location, match) => {
  const areDetails = areDetailsVisible(match)
  const { pathname, search } = location

  if (areDetails) {
    return `${pathname.split('/details')[0]}${search}`
  }
}

export default getUrlWithoutDetailsPart
