import { pluralize } from 'utils/pluralize'

export function computeSelectedOffersLabel(offersLength: number) {
  return offersLength > 500
    ? '500+ offres sélectionnées'
    : `${pluralize(offersLength, 'offre sélectionnée')}`
}
