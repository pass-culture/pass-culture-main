import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOfferStockResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import useNotification from 'hooks/useNotification'
import { serializeStockEvents } from 'pages/IndividualOfferWizard/Stocks/serializeStockEvents'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { getStockWarningText } from '../SummaryScreen/StockSection/StockSection'
import { StockThingSection } from '../SummaryScreen/StockSection/StockThingSection/StockThingSection'

import { RecurrenceSummary } from './RecurrenceSummary'
import styles from './StocksSummary.module.scss'

export const StocksSummaryScreen = () => {
  const { offer, subCategories } = useIndividualOfferContext()
  const [isLoading, setIsLoading] = useState(false)
  const [stocksEvent, setStocksEvent] = useState<StocksEvent[]>([])
  const [stockThing, setStocksThings] = useState<GetOfferStockResponseModel>()
  const notify = useNotification()

  useEffect(() => {
    async function loadStocks() {
      if (offer) {
        setIsLoading(true)
        try {
          const response = await api.getStocks(offer.id)

          if (offer.isEvent) {
            setStocksEvent(serializeStockEvents(response.stocks))
          } else {
            setStocksThings(response.stocks[0])
          }
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
  }, [notify, offer])

  if (offer === null || isLoading) {
    return <Spinner />
  }

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  const stockWarningText = getStockWarningText(offer)

  const canBeDuo = subCategories.find(
    (subcategory) => subcategory.id === offer.subcategoryId
  )?.canBeDuo

  return (
    <SummarySection
      title={offer.isEvent ? 'Dates et capacité' : 'Stocks et prix'}
      editLink={editLink}
      aria-label="Modifier les stocks et prix"
    >
      {stockWarningText && (
        <SummaryDescriptionList
          className={styles['stock-section-warning']}
          descriptions={[{ text: stockWarningText }]}
        />
      )}

      {offer.isEvent ? (
        <RecurrenceSummary offer={offer} stocks={stocksEvent} />
      ) : (
        <StockThingSection
          stock={stockThing}
          canBeDuo={canBeDuo}
          isDuo={offer.isDuo}
        />
      )}
    </SummarySection>
  )
}
