import React, { useEffect, useState } from 'react'

import useAnalytics from 'components/hooks/useAnalytics'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ROOT_PATH } from 'utils/config'

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
  const [showAllStocks, setShowAllStocks] = useState(false)
  const [displayedStocks, setDisplayedStocks] = useState(
    stocks.slice(0, NB_UNFOLDED_STOCK)
  )

  useEffect(() => {
    setDisplayedStocks(
      showAllStocks ? [...stocks] : stocks.slice(0, NB_UNFOLDED_STOCK)
    )
  }, [showAllStocks])

  const iconName = showAllStocks ? 'ico-arrow-up-b' : 'ico-arrow-down-b'
  const editLink = isCreation
    ? `/offre/${offerId}/individuel/creation/stocks`
    : `/offre/${offerId}/individuel/stocks`
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
          Icon={() => <img src={`${ROOT_PATH}/icons/${iconName}.svg`} />}
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
