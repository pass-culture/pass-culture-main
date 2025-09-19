import { useLocation } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  StockStatsResponseModel,
} from '@/apiClient/v1'
import {
  GET_STOCK_STATISTICS_QUERY_KEY,
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
  const isOnboarding = pathname.includes('onboarding')
  const notification = useNotification()

  const departmentCode = getDepartmentCode(offer)

  // Conditional SWR queries (only one runs depending on isEvent)
  const { data: stocksResp, isLoading: isStocksLoading } = useSWR(
    offer.isEvent ? null : [GET_STOCKS_QUERY_KEY, offer.id],
    () => api.getStocks(offer.id),
    {
      revalidateOnFocus: false,
      onError: () => {
        notification.error(
          'Une erreur est survenue lors de la récupération des informations de votre stock'
        )
      },
    }
  )

  const { data: stocksEventsStats, isLoading: isStatsLoading } =
    useSWR<StockStatsResponseModel>(
      offer.isEvent ? [GET_STOCK_STATISTICS_QUERY_KEY, offer.id] : null,
      () => api.getStocksStats(offer.id),
      {
        revalidateOnFocus: false,
        onError: () => {
          notification.error(
            'Une erreur est survenue lors de la récupération des informations de vos stocks'
          )
        },
      }
    )

  const isLoading = isStocksLoading || isStatsLoading
  if (isLoading) {
    return <Spinner />
  }

  const stockThing: GetOfferStockResponseModel | undefined =
    stocksResp?.stocks?.[0]

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
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
          stocksStats={stocksEventsStats}
          departementCode={departmentCode}
        />
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
