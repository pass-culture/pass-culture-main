import get from 'lodash.get'

function checkIfOfferIsTiteLiveGenerated(offer) {
  const lastProviderName = get(offer, 'lastProvider.name')
  if (lastProviderName !== undefined) {
    return (
      get(offer, 'lastProvider.name')
        .toLowerCase()
        .indexOf('titelive') !== -1
    )
  }
  return false
}

export default checkIfOfferIsTiteLiveGenerated
