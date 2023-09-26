import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { SummaryLayout } from 'components/SummaryLayout'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import { formatPrice } from 'utils/formatPrice'

import styles from './PriceCategoriesSection.module.scss'

interface Props {
  offer: IndividualOffer
  canBeDuo?: boolean
}

export const PriceCategoriesSection = ({ offer, canBeDuo }: Props) => {
  const mode = useOfferWizardMode()

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.TARIFS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
  })

  return (
    <SummaryLayout.Section
      title="Tarifs"
      editLink={editLink}
      aria-label="Modifier les tarifs de l’offre"
    >
      {offer.priceCategories?.map(priceCategory => (
        <div key={priceCategory.id} className={styles['price-category']}>
          {formatPrice(priceCategory.price)} - {priceCategory.label}
        </div>
      ))}
      {canBeDuo && (
        <SummaryLayout.Row
          title='Accepter les réservations "Duo"'
          description={offer.isDuo ? 'Oui' : 'Non'}
        />
      )}
    </SummaryLayout.Section>
  )
}
