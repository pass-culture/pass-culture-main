/* istanbul ignore file: DEBT, TO FIX */
import cn from 'classnames'
import React, { useState } from 'react'

import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import { ReactComponent as ArrowIcon } from 'icons/ico-arrow-up-b.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from '../StockSection.module.scss'

import { StockEventItem } from './StockEventItem'

const NB_UNFOLDED_STOCK = 2

interface IStockEventSectionProps {
  offer: IOfferIndividual
}

const sortStocks = (
  a: IOfferIndividualStock,
  b: IOfferIndividualStock
): number => {
  const aDate =
    a.beginningDatetime !== null ? new Date(a.beginningDatetime) : a.dateCreated
  const bDate =
    b.beginningDatetime !== null ? new Date(b.beginningDatetime) : b.dateCreated
  return aDate < bDate ? 1 : -1
}

const StockEventSection = ({ offer }: IStockEventSectionProps) => {
  const [showAllStocks, setShowAllStocks] = useState(false)
  if (!offer.isEvent || offer.stocks.length === 0) {
    return null
  }
  const sortedStocks = offer.stocks.sort(sortStocks)

  const displayedStocks = showAllStocks
    ? [...sortedStocks]
    : sortedStocks.slice(0, NB_UNFOLDED_STOCK)

  return (
    <>
      {displayedStocks.map(stock => {
        const priceCategory = offer.priceCategories?.find(
          priceCategory => priceCategory.id === stock.priceCategoryId
        )

        return (
          <StockEventItem
            key={`stock-${stock.id}`}
            className={styles['stock-event-item']}
            beginningDatetime={stock.beginningDatetime}
            price={stock.price}
            priceCategory={priceCategory}
            quantity={stock.quantity}
            bookingLimitDatetime={stock.bookingLimitDatetime}
            departmentCode={offer.venue.departmentCode}
          />
        )
      })}

      {sortedStocks.length > NB_UNFOLDED_STOCK && (
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
