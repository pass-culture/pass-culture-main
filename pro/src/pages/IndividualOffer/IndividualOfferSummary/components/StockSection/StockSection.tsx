import { useLocation } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  GET_STOCKS_EVENT_STATS_QUERY_KEY,
  GET_STOCKS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from '@/commons/hooks/useNotification'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { getStockWarningText } from '@/pages/IndividualOfferSummary/commons/getStockWarningText'
import { StockThingSection } from '@/pages/IndividualOfferSummary/components/StockThingSection/StockThingSection'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { RecurrenceSection } from './RecurrenceSection/RecurrenceSection'
import styles from './StockSection.module.scss'

export interface StockSectionProps {
  offer: GetIndividualOfferWithAddressResponseModel
  canBeDuo?: boolean
}

export const StockSection = ({
  offer,
  canBeDuo,
}: StockSectionProps): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const notification = useNotification()

  const departmentCode = getDepartmentCode(offer)
  const error =
    'Une erreur est survenue lors de la récupération des informations de votre stock'

  const getStockThingQuery = useSWR(
    !offer.isEvent ? [GET_STOCKS_QUERY_KEY, offer.id] : null,
    () => api.getStocks(offer.id),
    {
      onError: () => notification.error(error),
    }
  )
  const getStocksEventStatsQuery = useSWR(
    offer.isEvent ? [GET_STOCKS_EVENT_STATS_QUERY_KEY, offer.id] : null,
    () => api.getStocksStats(offer.id),
    {
      onError: () => notification.error(error),
    }
  )

  if (getStockThingQuery.isLoading || getStocksEventStatsQuery.isLoading) {
    return <Spinner />
  }

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: offer.isEvent
      ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
      : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    mode: OFFER_WIZARD_MODE.CREATION,
    isOnboarding,
  })

  const stockWarningText = getStockWarningText(offer)

  return (
    <SummarySection
      title={offer.isEvent ? 'Dates et capacités' : 'Stocks et prix'}
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
        <RecurrenceSection
          stocksStats={getStocksEventStatsQuery.data}
          departementCode={departmentCode}
        />
      ) : (
        <StockThingSection
          stock={getStockThingQuery.data?.stocks[0]}
          canBeDuo={canBeDuo}
          isDuo={offer.isDuo}
        />
      )}
    </SummarySection>
  )
}
