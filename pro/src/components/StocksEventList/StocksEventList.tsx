import cn from 'classnames'
import React, { useState, useCallback } from 'react'

import { PriceCategoryResponseModel } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { ResetIcon, TrashFilledIcon } from 'icons'
import searchIcon from 'icons/search-ico.svg'
import { getPriceCategoryOptions } from 'screens/OfferIndividual/StocksEventEdition/StocksEventEdition'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { BaseCheckbox } from 'ui-kit/form/shared'
import { BaseTimePicker } from 'ui-kit/form/TimePicker/BaseTimePicker'
import { Pagination } from 'ui-kit/Pagination'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { formatPrice } from 'utils/formatPrice'
import { formatLocalTimeDateString } from 'utils/timezone'

import { SortArrow } from './SortArrow'
import styles from './StocksEventList.module.scss'
import {
  SortingColumn,
  SortingMode,
  filterAndSortStocks,
} from './stocksFiltering'

export const STOCKS_PER_PAGE = 20

export interface StocksEvent {
  id?: string
  beginningDatetime: string
  bookingLimitDatetime: string
  priceCategoryId: number
  quantity: number | null
}

interface StocksEventListProps {
  stocks: StocksEvent[]
  priceCategories: PriceCategoryResponseModel[]
  className?: string
  departmentCode: string
  offerId: number
  setStocks: (stocks: StocksEvent[]) => void
}

const StocksEventList = ({
  stocks,
  priceCategories,
  className,
  departmentCode,
  offerId,
  setStocks,
}: StocksEventListProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const [isCheckedArray, setIsCheckedArray] = useState<boolean[]>(
    Array(stocks.length).fill(false)
  )
  const priceCategoryOptions = getPriceCategoryOptions(priceCategories)
  const areFiltersEnabled = useActiveFeature('WIP_RECURRENCE_FILTERS')

  const [currentSortingColumn, setCurrentSortingColumn] =
    useState<SortingColumn | null>(null)
  const [currentSortingMode, setCurrentSortingMode] = useState<SortingMode>(
    SortingMode.NONE
  )
  const [dateFilter, setDateFilter] = useState<Date | null>(null)
  const [hourFilter, setHourFilter] = useState<Date | null>(null)
  const [priceCategoryFilter, setPriceCategoryFilter] = useState('')

  const onHeaderClick = (headerName: SortingColumn) => {
    if (currentSortingColumn !== headerName) {
      setCurrentSortingColumn(headerName)
      setCurrentSortingMode(SortingMode.ASC)
      return
    } else {
      if (currentSortingMode === SortingMode.ASC) {
        setCurrentSortingMode(SortingMode.DESC)
      } else if (currentSortingMode === SortingMode.DESC) {
        setCurrentSortingMode(SortingMode.NONE)
      } else {
        setCurrentSortingMode(SortingMode.ASC)
      }
    }
  }

  const [page, setPage] = useState(1)
  const previousPage = useCallback(() => setPage(page => page - 1), [])
  const nextPage = useCallback(() => setPage(page => page + 1), [])
  const filteredStocks = filterAndSortStocks(
    stocks,
    priceCategories,
    currentSortingColumn,
    currentSortingMode,
    { dateFilter, hourFilter, priceCategoryFilter }
  )
  const stocksPage = filteredStocks.slice(
    (page - 1) * STOCKS_PER_PAGE,
    page * STOCKS_PER_PAGE
  )
  const pageCount = Math.ceil(filteredStocks.length / STOCKS_PER_PAGE)
  const areAllChecked = isCheckedArray.every(isChecked => isChecked)

  const handleOnChangeSelected = (index: number) => {
    const newArray = isCheckedArray.map(isChecked => isChecked)
    newArray[index] = !newArray[index]
    setIsCheckedArray(newArray)
  }

  const handleOnChangeSelectAll = () => {
    if (areAllChecked) {
      setIsCheckedArray(filteredStocks.map(() => false))
    } else {
      setIsCheckedArray(filteredStocks.map(() => true))
    }
  }

  const onFilterChange = () => {
    setPage(1)
    setIsCheckedArray(stocks.map(() => false))
  }

  const onDeleteStock = (index: number) => {
    // handle checkbox selection
    const newArray = [...isCheckedArray]
    newArray.splice(index, 1)
    setIsCheckedArray(newArray)

    stocks.splice(index, 1)
    setStocks([...stocks])
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.STOCKS,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STOCK_EVENT_DELETE,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
    })
    if (stocks.length % STOCKS_PER_PAGE === 0 && page === pageCount) {
      previousPage()
    }
    notify.success('1 occurrence a été supprimée')
  }

  const onBulkDelete = () => {
    const newStocks = stocks.filter((stock, index) => !isCheckedArray[index])
    const deletedStocksCount = stocks.length - newStocks.length
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.STOCKS,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STOCK_EVENT_BULK_DELETE,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
      deletionCount: `${stocks.length - newStocks.length}`,
    })
    setIsCheckedArray(stocks.map(() => false))
    setStocks([...newStocks])

    const newLastPage = Math.ceil(newStocks.length / STOCKS_PER_PAGE)
    if (
      deletedStocksCount >= stocks.length % STOCKS_PER_PAGE &&
      page > newLastPage
    ) {
      setPage(newLastPage)
    }
    notify.success(
      deletedStocksCount === 1
        ? '1 occurrence a été supprimée'
        : `${deletedStocksCount} occurrences ont été supprimées`
    )
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
    <div className={className}>
      <div className={styles['select-all-container']}>
        <BaseCheckbox
          label="Tout sélectionner"
          checked={areAllChecked}
          onChange={handleOnChangeSelectAll}
        />

        <div>
          {stocks.length} occurence{stocks.length !== 1 && 's'}
        </div>
      </div>

      <table className={styles['stock-event-table']}>
        <caption className={styles['table-caption']}>
          Liste des dates et capacités
        </caption>
        <thead>
          <tr>
            <th
              scope="col"
              className={cn(styles['date-column'], styles['header'])}
            >
              <span className={styles['header-name']}>Date</span>
              {areFiltersEnabled && (
                <>
                  <SortArrow
                    onClick={() => onHeaderClick(SortingColumn.DATE)}
                    sortingMode={
                      currentSortingColumn === SortingColumn.DATE
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />

                  <div className={cn(styles['filter-input'])}>
                    <BaseDatePicker
                      onChange={date => {
                        setDateFilter(date)
                        onFilterChange()
                      }}
                      value={dateFilter}
                      filterVariant
                      aria-label="Filtrer par date"
                    />
                  </div>
                </>
              )}
            </th>

            <th
              scope="col"
              className={cn(styles['time-column'], styles['header'])}
            >
              <span className={styles['header-name']}>Horaire</span>
              {areFiltersEnabled && (
                <>
                  <SortArrow
                    onClick={() => onHeaderClick(SortingColumn.HOUR)}
                    sortingMode={
                      currentSortingColumn === SortingColumn.HOUR
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                  <div className={cn(styles['filter-input'])}>
                    <BaseTimePicker
                      onChange={date => {
                        setHourFilter(date)
                        onFilterChange()
                      }}
                      value={hourFilter}
                      filterVariant
                      aria-label="Filtrer par horaire"
                    />
                  </div>
                </>
              )}
            </th>

            <th scope="col" className={styles['header']}>
              <span className={styles['header-name']}>Tarif</span>
              {areFiltersEnabled && (
                <>
                  <SortArrow
                    onClick={() => onHeaderClick(SortingColumn.PRICE_CATEGORY)}
                    sortingMode={
                      currentSortingColumn === SortingColumn.PRICE_CATEGORY
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                  <div className={cn(styles['filter-input'])}>
                    <SelectInput
                      name="priceCategoryFilter"
                      defaultOption={{ label: '', value: '' }}
                      options={priceCategoryOptions}
                      value={priceCategoryFilter}
                      onChange={event => {
                        setPriceCategoryFilter(event.target.value)
                        onFilterChange()
                      }}
                      filterVariant
                      aria-label="Filtrer par tarif"
                    />
                  </div>
                </>
              )}
            </th>

            <th
              scope="col"
              className={cn(
                styles['booking-limit-date-column'],
                styles['header']
              )}
            >
              <span className={styles['header-name']}>
                Date limite
                <br />
                de réservation
              </span>
              {areFiltersEnabled && (
                <>
                  <SortArrow
                    onClick={() =>
                      onHeaderClick(SortingColumn.BOOKING_LIMIT_DATETIME)
                    }
                    sortingMode={
                      currentSortingColumn ===
                      SortingColumn.BOOKING_LIMIT_DATETIME
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                  <div className={cn(styles['filter-input'])}>&nbsp;</div>
                </>
              )}
            </th>

            <th
              scope="col"
              className={cn(styles['quantity-column'], styles['header'])}
            >
              <span className={styles['header-name']}>Places</span>
              {areFiltersEnabled && (
                <>
                  <SortArrow
                    onClick={() => onHeaderClick(SortingColumn.QUANTITY)}
                    sortingMode={
                      currentSortingColumn === SortingColumn.QUANTITY
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                  <div className={cn(styles['filter-input'])}>&nbsp;</div>
                </>
              )}
            </th>
            <th className={cn(styles['actions-column'], styles['header'])} />
          </tr>
        </thead>

        <tbody>
          {filteredStocks.length !== stocks.length && (
            <tr>
              <td colSpan={6}>
                <div className={styles['filtered-data-row']}>
                  <div>
                    Résultat de recherche :{' '}
                    <strong>
                      {filteredStocks.length} occurence
                      {filteredStocks.length !== 1 && 's'}
                    </strong>
                  </div>

                  <div>
                    <Button
                      Icon={ResetIcon}
                      variant={ButtonVariant.TERNARY}
                      onClick={() => {
                        setDateFilter(null)
                        setHourFilter(null)
                        setPriceCategoryFilter('')
                        onFilterChange()
                      }}
                    >
                      Réinitialiser les filtres
                    </Button>
                  </div>
                </div>
              </td>
            </tr>
          )}

          {stocksPage.map((stock, index) => {
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

            const currentStockIndex = (page - 1) * STOCKS_PER_PAGE + index

            return (
              <tr key={index} className={styles['row']}>
                <td className={styles['data']}>
                  <div
                    className={cn(
                      styles['date-cell-wrapper'],
                      styles['capitalize']
                    )}
                  >
                    <BaseCheckbox
                      checked={isCheckedArray[currentStockIndex]}
                      onChange={() => handleOnChangeSelected(currentStockIndex)}
                      label=""
                    />

                    <div className={styles['day']}>
                      <strong>{beginningDay}</strong>
                    </div>
                    <div>{beginningDate}</div>
                  </div>
                </td>
                <td className={styles['data']}>{beginningHour}</td>
                <td className={styles['data']}>{price}</td>
                <td className={styles['data']}>{bookingLimitDate}</td>
                <td className={styles['data']}>
                  {stock.quantity === null ? 'Illimité' : stock.quantity}
                </td>
                <td className={cn(styles['data'], styles['clear-icon'])}>
                  <Button
                    variant={ButtonVariant.TERNARY}
                    onClick={() => onDeleteStock(currentStockIndex)}
                    Icon={TrashFilledIcon}
                    hasTooltip
                  >
                    Supprimer
                  </Button>
                </td>
              </tr>
            )
          })}

          {filteredStocks.length === 0 && (
            <tr>
              <td colSpan={6} className={styles['no-data']}>
                <SvgIcon
                  src={searchIcon}
                  alt=""
                  className={styles['no-data-icon']}
                  viewBox="0 0 20 20"
                />
                <div className={styles['no-data-message']}>
                  Aucune occurence trouvée
                </div>
                <div className={styles['no-data-help']}>
                  Vous pouvez modifier vos filtres pour lancer une nouvelle
                  recherche
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <Pagination
        currentPage={page}
        pageCount={pageCount}
        onPreviousPageClick={previousPage}
        onNextPageClick={nextPage}
      />

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
    </div>
  )
}

export default StocksEventList
