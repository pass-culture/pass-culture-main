import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { SummaryLayout } from 'components/SummaryLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'

import { getStockWarningText } from '../SummaryScreen/StockSection/StockSection'
import StockThingSection from '../SummaryScreen/StockSection/StockThingSection/StockThingSection'

import { RecurrenceSummary } from './RecurrenceSummary'
import styles from './StocksSummary.module.scss'

export const StocksSummaryScreen = () => {
  const { offer, subCategories } = useIndividualOfferContext()

  if (offer === null) {
    return null
  }
  const canBeDuo = subCategories.find(
    subcategory => subcategory.id === offer.subcategoryId
  )?.canBeDuo

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  const stockWarningText = getStockWarningText(offer)

  return (
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
        <RecurrenceSummary offer={offer} />
      ) : (
        <StockThingSection offer={offer} canBeDuo={canBeDuo} />
      )}
    </SummaryLayout.Section>
  )
}
