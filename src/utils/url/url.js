export const versoUrl = (offerId, mediationId) => {
  const urlElements = ['', 'decouverte', offerId, 'verso']

  if (mediationId) {
    urlElements.splice(3, 0, mediationId)
  }

  return urlElements.join('/')
}
