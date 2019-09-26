import { PROVIDER_NAMES } from '../../../utils/providers'

const isTiteLiveOffer = offer => {
  if (offer == null) {
    return false
  }

  const { lastProvider } = offer
  if (lastProvider === null) {
    return false
  }

  const { name: lastProviderName } = lastProvider
  const lastProviderNameAsLowerCase = lastProviderName.toLowerCase()
  return lastProviderNameAsLowerCase.includes(PROVIDER_NAMES['TiteLive'])
}

export default isTiteLiveOffer
