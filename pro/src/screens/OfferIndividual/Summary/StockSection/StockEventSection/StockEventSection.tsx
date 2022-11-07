/* istanbul ignore file: DEBT, TO FIX */
import cn from 'classnames'
import React, { useEffect, useState } from 'react'

import { ReactComponent as ArrowIcon } from 'icons/ico-arrow-up-b.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from '../StockSection.module.scss'

import type { IStockEventItemProps } from './StockEventItem'
import { StockEventItem } from './StockEventItem'

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

  return (
    <>
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
              className={
                /* istanbul ignore next: DEBT, TO FIX */
                cn(styles['stock-event-item-display-more-icon'], {
                  [styles['stock-event-item-display-more-icon-down']]:
                    !showAllStocks,
                })
              }
            />
          )}
          variant={ButtonVariant.TERNARY}
          onClick={() => setShowAllStocks(!showAllStocks)}
        >
          {showAllStocks ? 'Afficher moins de dates' : 'Afficher plus de dates'}
        </Button>
      )}
    </>
  )
}

export default StockEventSection
