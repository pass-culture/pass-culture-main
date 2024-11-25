import { pluralize } from 'commons/utils/pluralize'

export function computeSelectedOffersLabel(offersLength: number) {
  return offersLength > 500
    ? '500+ offres sélectionnées'
    : `${pluralize(offersLength, 'offre sélectionnée')}`
}
