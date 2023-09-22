import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { SummaryLayout } from 'components/SummaryLayout'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'

import { RecurrenceSection } from './RecurrenceSection'
import styles from './StockSection.module.scss'
import { StockThingSection } from './StockThingSection'

export interface StockSectionProps {
  offer: IndividualOffer
  canBeDuo?: boolean
}

const StockSection = ({ offer, canBeDuo }: StockSectionProps): JSX.Element => {
  const mode = useOfferWizardMode()

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
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
        aria-label="Modifier les stocks et prix"
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
