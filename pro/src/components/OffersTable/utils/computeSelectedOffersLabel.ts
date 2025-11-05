import { MAX_OFFERS_TO_DISPLAY } from '@/commons/core/Offers/constants'
import { pluralizeFr } from '@/commons/utils/pluralize'

export function computeSelectedOffersLabel(offersLength: number) {
  return offersLength > MAX_OFFERS_TO_DISPLAY
    ? `${MAX_OFFERS_TO_DISPLAY}+ offres sélectionnées`
    : `${offersLength} ${pluralizeFr(offersLength, 'offre sélectionnée', 'offres sélectionnées')}`
}
