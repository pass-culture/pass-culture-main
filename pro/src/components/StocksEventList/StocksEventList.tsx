import cn from 'classnames'
import React, { useState } from 'react'

import { PriceCategoryResponseModel } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { ClearIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { formatPrice } from 'utils/formatPrice'
import { formatLocalTimeDateString } from 'utils/timezone'

import styles from './StocksEventList.module.scss'

export interface IStocksEvent {
  id?: string
  beginningDatetime: string
  bookingLimitDatetime: string
  priceCategoryId: number
  quantity: number | null
}

interface IStocksEventListProps {
  stocks: IStocksEvent[]
  priceCategories: PriceCategoryResponseModel[]
  className?: string
  departmentCode?: string
  setStocks: (stocks: IStocksEvent[]) => void
}

const StocksEventList = ({
  stocks,
  priceCategories,
  className,
  departmentCode,
  setStocks,
}: IStocksEventListProps): JSX.Element => {
  const [isCheckedArray, setIsCheckedArray] = useState(stocks.map(() => false))
  const areAllChecked = isCheckedArray.every(isChecked => isChecked)

  const handleOnChangeSelected = (index: number) => {
    const newArray = isCheckedArray.map(isChecked => isChecked)
    newArray[index] = !newArray[index]
    setIsCheckedArray(newArray)
  }

  const handleOnChangeSelectAll = () => {
    if (areAllChecked) {
      setIsCheckedArray(stocks.map(() => false))
    } else {
      setIsCheckedArray(stocks.map(() => true))
    }
  }

  const onDeleteStock = (index: number) => {
    stocks.splice(index, 1)
    setStocks([...stocks])
  }

  const onBulkDelete = () => {
    const newStocks = stocks.filter((stock, index) => !isCheckedArray[index])
    setIsCheckedArray(stocks.map(() => false))
    setStocks([...newStocks])
  }

  const onCancelClick = () => {
    setIsCheckedArray(stocks.map(() => false))
  }

  const selectedDateText =
    isCheckedArray.filter(e => e === true).length > 1
      ? `${isCheckedArray.filter(e => e === true).length} dates sélectionnées`
      : '1 date sélectionnée'

  const isAtLeastOneStockChecked = isCheckedArray.some(e => e)

  return (
    <>
      <table className={cn(styles['stock-event-table'], className)}>
        <thead>
          <tr>
            <th className={cn(styles['first-column'], styles['header'])}>
              <input
                checked={areAllChecked}
                onChange={handleOnChangeSelectAll}
                type="checkbox"
                aria-label="Sélectionner toutes les lignes"
              />
            </th>
            <th className={styles['header']}>Date</th>
            <th className={styles['header']}>Horaire</th>
            <th className={styles['header']}>Places</th>
            <th className={styles['header']}>Tarif</th>
            <th className={styles['header']}>Limite de réservation</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock, index) => {
            const beginningDay = formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              'eee'
            ).replace('.', '')

            const beginningDate = formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              'dd/MM/yyyy'
            )

            const beginningHour = formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              'HH:mm'
            )
            const bookingLimitDate = formatLocalTimeDateString(
              stock.bookingLimitDatetime,
              departmentCode,
              'dd/MM/yyyy'
            )
            const priceCategory = priceCategories.find(
              pC => pC.id === stock.priceCategoryId
            )

            let price = ''
            /* istanbul ignore next priceCategory would never be null */
            if (priceCategory) {
              price = `${formatPrice(priceCategory.price)} - ${
                priceCategory?.label
              }`
            }
            return (
              <tr key={index}>
                <td className={styles['data']}>
                  <input
                    checked={isCheckedArray[index]}
                    onChange={() => handleOnChangeSelected(index)}
                    type="checkbox"
                  />
                </td>
                <td className={cn(styles['data'], styles['with-border'])}>
                  <b>{beginningDay} </b>
                  {beginningDate}
                </td>
                <td className={cn(styles['data'], styles['with-border'])}>
                  {beginningHour}
                </td>
                <td className={cn(styles['data'], styles['with-border'])}>
                  {stock.quantity === null ? 'Illimité' : stock.quantity}
                </td>
                <td className={cn(styles['data'], styles['with-border'])}>
                  {price}
                </td>
                <td className={cn(styles['data'], styles['with-border'])}>
                  {bookingLimitDate}
                </td>
                <td className={cn(styles['data'], styles['clear-icon'])}>
                  <Button
                    variant={ButtonVariant.TERNARY}
                    onClick={() => onDeleteStock(index)}
                    Icon={ClearIcon}
                    iconPosition={IconPositionEnum.CENTER}
                    hasTooltip
                  >
                    Supprimer le stock
                  </Button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      {isAtLeastOneStockChecked && (
        <ActionsBarSticky className={styles['actions']}>
          <ActionsBarSticky.Left>{selectedDateText}</ActionsBarSticky.Left>
          <ActionsBarSticky.Right>
            {
              <>
                <Button
                  onClick={onCancelClick}
                  variant={ButtonVariant.SECONDARY}
                >
                  Annuler
                </Button>
                <Button onClick={onBulkDelete}>Supprimer ces dates</Button>
              </>
            }
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      )}
    </>
  )
}

export default StocksEventList
