import { ICONS_URL } from '../../../../../utils/config'
import OFFER_TYPE_PICTO from './offerTypePicto'

const findOfferPictoPathByOfferType = subcategory => {
  if (!subcategory) {
    return null
  }

  const searchGroup = subcategory.searchGroup
  const picto = OFFER_TYPE_PICTO[searchGroup]

  return `${ICONS_URL}/picto-${picto}.svg`
}

export default findOfferPictoPathByOfferType
