import { ICONS_URL } from '../../../../../utils/config'
import OFFER_TYPE_PICTO from './offerTypePicto'

const findOfferPictoPathByOfferType = subcategory => {
  if (!subcategory) {
    return null
  }

  const searchGroupName = subcategory.searchGroupName
  const picto = OFFER_TYPE_PICTO[searchGroupName]

  return `${ICONS_URL}/picto-${picto}.svg`
}

export default findOfferPictoPathByOfferType
