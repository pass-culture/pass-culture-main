import React from 'react'

import { OfferStatus } from 'apiClient/v1'
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

import { RecurrenceSection } from './RecurrenceSection'
import styles from './StockSection.module.scss'
import { StockThingSection } from './StockThingSection'

export interface StockSectionProps {
  offer: IndividualOffer
  canBeDuo?: boolean
}

const StockSection = ({ offer, canBeDuo }: StockSectionProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()

  const logEditEvent = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.SUMMARY,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft:
        mode === OFFER_WIZARD_MODE.CREATION || mode === OFFER_WIZARD_MODE.DRAFT,
      offerId: offer.id,
    })
  }

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode,
  })

  const hasNoStock = offer.stocks.length === 0

  const stockWarningText = hasNoStock
    ? 'Vous n’avez aucun stock renseigné.'
    : // @ts-expect-error Other OfferStatus make stockWarningText be undefined wich is expected
      {
        [OfferStatus.SOLD_OUT]: 'Votre stock est épuisé.',
        [OfferStatus.EXPIRED]: 'Votre stock est expiré.',
      }[offer.status]

  return (
    <>
      <SummaryLayout.Section
        title={offer.isEvent ? 'Dates et capacité' : 'Stocks et prix'}
        editLink={editLink}
        onLinkClick={logEditEvent}
        aria-label="Modifier stock et prix"
      >
        {stockWarningText && (
          <SummaryLayout.Row
            className={styles['stock-section-warning']}
            description={stockWarningText}
          />
        )}

        {offer.isEvent ? (
          <RecurrenceSection offer={offer} />
        ) : (
          <StockThingSection offer={offer} canBeDuo={canBeDuo} />
        )}
      </SummaryLayout.Section>
    </>
  )
}

export default StockSection
