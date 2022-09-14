import cn from 'classnames'
import React, { useEffect, useState } from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { ReactComponent as ArrowIcon } from 'icons/ico-arrow-up-b.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import type { IStockEventItemProps } from './StockEventItem'
import { StockEventItem } from './StockEventItem'
import styles from './StockEventSection.module.scss'

const NB_UNFOLDED_STOCK = 2

export interface IStockEventSectionProps {
  stocks: IStockEventItemProps[]
  isCreation: boolean
  offerId: string
}

const StockEventSection = ({
  stocks,
  isCreation,
  offerId,
}: IStockEventSectionProps): JSX.Element => {
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const [showAllStocks, setShowAllStocks] = useState(false)
  const [displayedStocks, setDisplayedStocks] = useState(
    stocks.slice(0, NB_UNFOLDED_STOCK)
  )

  useEffect(() => {
    setDisplayedStocks(
      showAllStocks ? [...stocks] : stocks.slice(0, NB_UNFOLDED_STOCK)
    )
  }, [showAllStocks])

  const stocksUrls = isOfferFormV3
    ? {
        creation: `/offre/:${offerId}/v3/creation/individuelle/stocks`,
        edition: `/offre/${offerId}/v3/individuelle/stocks`,
      }
    : {
        creation: `/offre/${offerId}/individuel/creation/stocks`,
        edition: `/offre/${offerId}/individuel/stocks`,
      }
  const editLink = isCreation ? stocksUrls.creation : stocksUrls.edition
  const { logEvent } = useAnalytics()
  const logEditEvent = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: !isCreation,
    })
  }
  return (
    <SummaryLayout.Section
      title="Stocks et prix"
      editLink={editLink}
      onLinkClick={logEditEvent}
    >
      {displayedStocks.map((s, k) => (
        <StockEventItem
          key={`stock-${k}`}
          className={styles['stock-event-item']}
          beginningDatetime={s.beginningDatetime}
          price={s.price}
          quantity={s.quantity}
          bookingLimitDatetime={s.bookingLimitDatetime}
          departmentCode={s.departmentCode}
        />
      ))}

      {stocks.length > NB_UNFOLDED_STOCK && (
        <Button
          className={styles['stock-event-item-display-more']}
          Icon={() => (
            <ArrowIcon
              className={cn(styles['stock-event-item-display-more-icon'], {
                [styles['stock-event-item-display-more-icon-down']]:
                  !showAllStocks,
              })}
            />
          )}
          variant={ButtonVariant.TERNARY}
          onClick={() => setShowAllStocks(!showAllStocks)}
        >
          {showAllStocks ? 'Afficher moins de dates' : 'Afficher plus de dates'}
        </Button>
      )}
    </SummaryLayout.Section>
  )
}

export default StockEventSection
