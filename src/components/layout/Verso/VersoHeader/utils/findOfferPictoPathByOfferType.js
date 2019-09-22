import { ICONS_URL } from '../../../../../utils/config'
import OFFER_TYPE_PICTO from './offerTypePicto'

const findOfferPictoPathByOfferType = offerType => {
  if (!offerType) {
    return null
  }

  const category = offerType.split('.')
  const picto = OFFER_TYPE_PICTO[category[1]]

  return `${ICONS_URL}/picto-${picto}.svg`
}

export default findOfferPictoPathByOfferType
