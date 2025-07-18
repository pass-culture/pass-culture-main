import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_STOCKS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from 'commons/hooks/useNotification'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { serializeStockEvents } from 'pages/IndividualOfferWizard/Stocks/serializeStockEvents'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { getStockWarningText } from '../../../pages/IndividualOfferSummary/IndividualOfferSummary/components/StockSection/StockSection'
import { StockThingSection } from '../../../pages/IndividualOfferSummary/IndividualOfferSummary/components/StockSection/StockThingSection/StockThingSection'

import { RecurrenceSummary } from './RecurrenceSummary'
import styles from './StocksSummary.module.scss'

export const StocksSummaryScreen = () => {
  const { offer, subCategories } = useIndividualOfferContext()
  const notify = useNotification()

  const getStocksQuery = useSWR(
    offer?.id ? [GET_STOCKS_QUERY_KEY, offer.id] : null,
    ([, offerId]) => api.getStocks(offerId),
    {
      onError: () => {
        notify.error(
          'Une erreur est survenue lors du chargement de vos stocks.'
        )
      },
    }
  )

  if (offer === null || getStocksQuery.isLoading || !getStocksQuery.data) {
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
        <RecurrenceSummary
          offer={offer}
          stocks={serializeStockEvents(getStocksQuery.data.stocks)}
        />
      ) : (
        <StockThingSection
          stock={getStocksQuery.data.stocks[0]}
          canBeDuo={canBeDuo}
          isDuo={offer.isDuo}
        />
      )}
    </SummarySection>
  )
}
