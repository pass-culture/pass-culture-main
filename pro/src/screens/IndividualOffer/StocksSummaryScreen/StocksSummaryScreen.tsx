import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { SummaryLayout } from 'components/SummaryLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import useNotification from 'hooks/useNotification'
import { serializeStockEvents } from 'pages/IndividualOfferWizard/Stocks/serializeStockEvents'

import { getStockWarningText } from '../SummaryScreen/StockSection/StockSection'
import StockThingSection from '../SummaryScreen/StockSection/StockThingSection/StockThingSection'

import { RecurrenceSummary } from './RecurrenceSummary'
import styles from './StocksSummary.module.scss'

export const StocksSummaryScreen = () => {
  const { offer } = useIndividualOfferContext()
  const [isLoading, setIsLoading] = useState(false)
  const [stocks, setStocks] = useState<StocksEvent[]>([])
  const notify = useNotification()

  useEffect(() => {
    async function loadStocks() {
      if (offer?.isEvent) {
        setIsLoading(true)
        try {
          const response = await api.getStocks(offer.id)

          setStocks(serializeStockEvents(response.stocks))
        } catch {
          notify.error(
            'Une erreur est survenue lors du chargement de vos stocks.'
          )
        }
        setIsLoading(false)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStocks()
  }, [])

  if (offer === null || isLoading) {
    return null
  }

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
        <RecurrenceSummary offer={offer} stocks={stocks} />
      ) : (
        <StockThingSection stock={offer.stocks[0]} />
      )}
    </SummaryLayout.Section>
  )
}
