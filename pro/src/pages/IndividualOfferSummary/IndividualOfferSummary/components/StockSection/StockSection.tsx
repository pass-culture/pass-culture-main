import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { api } from '@/apiClient//api'
import {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  StockStatsResponseModel,
} from '@/apiClient//v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
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
  const mode = useOfferWizardMode()
  const [isLoading, setIsLoading] = useState(false)
  const [stocksEventsStats, setStocksEventsStats] = useState<
    StockStatsResponseModel | undefined
  >(undefined)
  const [stockThing, setStockThing] = useState<GetOfferStockResponseModel>()
  const notification = useNotification()

  const departmentCode = getDepartmentCode(offer)

  useEffect(() => {
    async function getStockThing() {
      setIsLoading(true)
      try {
        const reponse = await api.getStocks(offer.id)
        setStockThing(reponse.stocks[0])
      } catch {
        notification.error(
          'Une erreur est survenue lors de la récupération des informations de votre stock'
        )
      }
      setIsLoading(false)
    }

    async function getStocksEventsStats() {
      setIsLoading(true)
      try {
        const reponse = await api.getStocksStats(offer.id)
        setStocksEventsStats(reponse)
      } catch {
        notification.error(
          'Une erreur est survenue lors de la récupération des informations de vos stocks'
        )
      }
      setIsLoading(false)
    }

    if (offer.isEvent) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getStocksEventsStats()
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getStockThing()
    }
  }, [notification, offer.id, offer.isEvent])

  if (isLoading) {
    return <Spinner />
  }

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
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
