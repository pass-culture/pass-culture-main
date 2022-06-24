import React, { useEffect, useState } from 'react'

import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import type { IStockEventItemProps } from './StockEventItem'
import { Icon } from '@mui/material'
import { ROOT_PATH } from 'utils/config'
import { StockEventItem } from './StockEventItem'
import { SummaryLayout } from 'new_components/SummaryLayout'
import styles from './StockEventSection.module.scss'

const NB_UNFOLDED_STOCK = 2

export interface IStockEventSectionProps {
  stocks: IStockEventItemProps[]
}

const StockEventSection = ({
  stocks,
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

  const iconName = showAllStocks ? 'ico-arrow-up-r' : 'ico-arrow-down-r'
  const showButtonIcon = <img src={`${ROOT_PATH}/icons/${iconName}.svg`} />

  return (
    <SummaryLayout.Section title="Stocks et prix">
      {displayedStocks.map((s, k) => (
        <StockEventItem
          key={`stock-${k}`}
          className={styles['stock-event-item']}
          beginningDateTime={s.beginningDateTime}
          price={s.price}
          quantity={s.quantity}
          bookingLimitDatetime={s.bookingLimitDatetime}
        />
      ))}

      {stocks.length > NB_UNFOLDED_STOCK && (
        <Button
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
