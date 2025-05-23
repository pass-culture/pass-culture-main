import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  OfferStatus,
  StockStatsResponseModel,
} from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { RecurrenceSection } from './RecurrenceSection/RecurrenceSection'
import styles from './StockSection.module.scss'
import { StockThingSection } from './StockThingSection/StockThingSection'

export const getStockWarningText = (offer: GetIndividualOfferResponseModel) => {
  if (!offer.hasStocks) {
    return 'Vous n’avez aucun stock renseigné.'
  }

  if (offer.status === OfferStatus.SOLD_OUT) {
    return 'Votre stock est épuisé.'
  }

  if (offer.status === OfferStatus.EXPIRED) {
    return 'Votre stock est expiré.'
  }

  return false
}

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
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
    isOnboarding,
  })

  const stockWarningText = getStockWarningText(offer)

  return (
    <>
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
    </>
  )
}
