const mapArgsToCacheKey = (state, offerId, mediationId, position) => {
  return `${offerId || ''}/${mediationId || ''}/${position || ''}`
}

export default mapArgsToCacheKey
