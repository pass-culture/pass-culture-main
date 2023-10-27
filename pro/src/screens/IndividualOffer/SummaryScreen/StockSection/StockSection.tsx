import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { OfferStatus, StockStatsResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { SummaryLayout } from 'components/SummaryLayout'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

import RecurrenceSection from './RecurrenceSection/RecurrenceSection'
import styles from './StockSection.module.scss'
import StockThingSection from './StockThingSection/StockThingSection'

export const getStockWarningText = (
  offerStatus: OfferStatus,
  stocksCount?: number | null
) => {
  if (!stocksCount) {
    return 'Vous n’avez aucun stock renseigné.'
  }

  if (offerStatus === OfferStatus.SOLD_OUT) {
    return 'Votre stock est épuisé.'
  }

  if (offerStatus === OfferStatus.EXPIRED) {
    return 'Votre stock est expiré.'
  }

  return false
}

export interface StockSectionProps {
  offer: IndividualOffer
  canBeDuo?: boolean
}

const StockSection = ({ offer, canBeDuo }: StockSectionProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const [isLoading, setIsLoading] = useState(false)
  const [stocksEventsStats, setStocksEventsStats] = useState<
    StockStatsResponseModel | undefined
  >(undefined)
  const notification = useNotification()

  useEffect(() => {
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
    }
  }, [])

  if (isLoading) {
    return <Spinner />
  }

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
  })

  const stockWarningText = getStockWarningText(
    offer.status,
    offer.isEvent ? stocksEventsStats?.stockCount : offer.stocks.length
  )

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
          <RecurrenceSection
            stocksStats={stocksEventsStats}
            departementCode={offer.venue.departementCode ?? ''}
          />
        ) : (
          <StockThingSection
            stock={offer.stocks[0]}
            canBeDuo={canBeDuo}
            isDuo={offer.isDuo}
          />
        )}
      </SummaryLayout.Section>
    </>
  )
}

export default StockSection
