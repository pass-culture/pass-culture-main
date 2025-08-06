import { MAX_OFFERS_TO_DISPLAY } from '@/commons/core/Offers/constants'
import { pluralize } from '@/commons/utils/pluralize'

export function computeSelectedOffersLabel(offersLength: number) {
  return offersLength > MAX_OFFERS_TO_DISPLAY
    ? `${MAX_OFFERS_TO_DISPLAY}+ offres sélectionnées`
    : `${pluralize(offersLength, 'offre sélectionnée')}`
}
