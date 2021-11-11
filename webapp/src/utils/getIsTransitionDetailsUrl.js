const getIsTransitionDetailsUrl = (match = {}) =>
  match.params && match.params.details === 'transition'

export default getIsTransitionDetailsUrl
