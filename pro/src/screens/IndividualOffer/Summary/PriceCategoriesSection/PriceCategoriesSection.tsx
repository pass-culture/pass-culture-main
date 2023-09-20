import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import { formatPrice } from 'utils/formatPrice'

import styles from './PriceCategoriesSection.module.scss'

interface Props {
  offer: IndividualOffer
  canBeDuo?: boolean
}

export const PriceCategoriesSection = ({ offer, canBeDuo }: Props) => {
  const { logEvent } = useAnalytics()
  const mode = useOfferWizardMode()

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.TARIFS,
    mode,
  })

  const logEditEvent = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.SUMMARY,
      to: OFFER_WIZARD_STEP_IDS.TARIFS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isDraft:
        mode === OFFER_WIZARD_MODE.CREATION || mode === OFFER_WIZARD_MODE.DRAFT,
      offerId: offer.id,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
    })
  }

  return (
    <SummaryLayout.Section
      title="Tarifs"
      editLink={editLink}
      onLinkClick={logEditEvent}
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
