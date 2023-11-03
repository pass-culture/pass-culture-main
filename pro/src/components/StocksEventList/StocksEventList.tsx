import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { PriceCategoryResponseModel, StocksOrderedBy } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import useNotification from 'hooks/useNotification'
import { usePaginationWithSearchParams } from 'hooks/usePagination'
import fullTrashIcon from 'icons/full-trash.svg'
import { getPriceCategoryOptions } from 'screens/IndividualOffer/StocksEventEdition/getPriceCategoryOptions'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { BaseCheckbox } from 'ui-kit/form/shared'
import { BaseTimePicker } from 'ui-kit/form/TimePicker/BaseTimePicker'
import { Pagination } from 'ui-kit/Pagination'
import { formatPrice } from 'utils/formatPrice'
import { pluralizeString } from 'utils/pluralize'
import {
  convertFromLocalTimeToVenueTimezoneInUtc,
  formatLocalTimeDateString,
} from 'utils/timezone'

import { FilterResultsRow } from './FilterResultsRow'
import { NoResultsRow } from './NoResultsRow'
import { SortArrow } from './SortArrow'
import styles from './StocksEventList.module.scss'

export const STOCKS_PER_PAGE = 20

export interface StocksEvent {
  id: number
  beginningDatetime: string
  bookingLimitDatetime: string
  priceCategoryId: number
  quantity: number | null
  bookingsQuantity: number
  isEventDeletable: boolean
}

export interface StocksEventListProps {
  stocks: StocksEvent[]
  priceCategories: PriceCategoryResponseModel[]
  className?: string
  departmentCode?: string | null
  offerId: number
  setStocks?: (stocks: StocksEvent[]) => void
  readonly?: boolean
  stockCount: number
}

const DELETE_STOCKS_CHUNK_SIZE = 50
function* chunks<T>(array: T[], n: number): Generator<T[], void> {
  for (let i = 0; i < array.length; i += n) {
    yield array.slice(i, i + n)
  }
}

const StocksEventList = ({
  stocks,
  priceCategories,
  className,
  departmentCode,
  offerId,
  setStocks,
  stockCount,
  readonly = false,
}: StocksEventListProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const [isCheckedArray, setIsCheckedArray] = useState<boolean[]>(
    Array(stocks.length).fill(false)
  )
  const priceCategoryOptions = getPriceCategoryOptions(priceCategories)

  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<StocksOrderedBy>()
  const [searchParams, setSearchParams] = useSearchParams()
  const { page, previousPage, nextPage, pageCount, firstPage, lastPage } =
    usePaginationWithSearchParams(STOCKS_PER_PAGE, stockCount)
  const date = searchParams.get('date')
  const time = searchParams.get('time')
  const priceCategoryId = searchParams.get('priceCategoryId')
  const [dateFilter, setDateFilter] = useState<string>(date ?? '')
  const [timeFilter, setTimeFilter] = useState<string>(time ?? '')
  const [priceCategoryIdFilter, setPriceCategoryIdFilter] = useState(
    priceCategoryId ?? ''
  )

  useEffect(() => {
    if (dateFilter) {
      searchParams.set('date', dateFilter)
    }
    if (timeFilter) {
      searchParams.set('time', timeFilter)
    }
    if (priceCategoryIdFilter) {
      searchParams.set('priceCategoryId', priceCategoryIdFilter)
    }
    if (currentSortingColumn) {
      searchParams.set('orderBy', currentSortingColumn)
    }
    if (currentSortingMode) {
      if (currentSortingMode === SortingMode.DESC) {
        searchParams.set('orderByDesc', '1')
      } else if (currentSortingMode === SortingMode.ASC) {
        searchParams.set('orderByDesc', '0')
      }
    }
    setSearchParams(searchParams)
  }, [
    dateFilter,
    timeFilter,
    priceCategoryIdFilter,
    currentSortingColumn,
    currentSortingMode,
  ])

  const onFilterChange = () => {
    setIsCheckedArray(stocks.map(() => false))
    firstPage()
  }

  const areAllChecked = isCheckedArray.every((isChecked) => isChecked)

  const handleOnChangeSelected = (index: number) => {
    const newArray = isCheckedArray.map((isChecked) => isChecked)
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

  const onDeleteStock = async (selectIndex: number, stockId: number) => {
    // handle checkbox selection
    const newArray = [...isCheckedArray]
    newArray.splice(selectIndex, 1)
    setIsCheckedArray(newArray)
    const stockIndex = stocks.findIndex((stock) => stock.id === stockId)

    stocks.splice(stockIndex, 1)
    setStocks?.([...stocks])
    await api.deleteStock(stockId)
    logEvent?.(Events.CLICKED_DELETE_STOCK, {
      offerId: offerId,
      stockId: stockId,
    })

    // FIX ME: this is broken
    // if it's still here in pull request, please block it :)
    if (stocks.length % STOCKS_PER_PAGE === 0 && page === pageCount) {
      previousPage()
    }
    notify.success('1 occurrence a été supprimée')
  }

  const onBulkDelete = async () => {
    const stocksIdToDelete = stocks
      .filter((stock, index) => isCheckedArray[index])
      .map((stock) => stock.id)

    const newStocks = stocks.filter(
      (stock) => !stocksIdToDelete.includes(stock.id)
    )

    logEvent?.(Events.CLICKED_BULK_DELETE_STOCK, {
      offerId: offerId,
      deletionCount: stocksIdToDelete.length,
    })
    setStocks?.([...newStocks])
    setIsCheckedArray(stocks.map(() => false))

    if (stocksIdToDelete.length > 0) {
      // If all stocks are checked without any stock unchecked,
      // use the delete all route with filters
      if (areAllChecked) {
        await api.deleteAllFilteredStocks(offerId, {
          date: dateFilter === '' ? null : dateFilter,
          time:
            hourFilter === ''
              ? null
              : convertFromLocalTimeToVenueTimezoneInUtc(
                  hourFilter,
                  departmentCode
                ),
          price_category_id:
            priceCategoryFilter === '' ? null : parseInt(priceCategoryFilter),
        })
      } else {
        // Otherwise, use the bulk delete stocks by id route
        await Promise.all(
          [...chunks(stocksIdToDelete, DELETE_STOCKS_CHUNK_SIZE)].map((ids) =>
            api.deleteStocks(offerId, { ids_to_delete: ids })
          )
        )
      }
    }

    const newLastPage = Math.ceil(newStocks.length / STOCKS_PER_PAGE)
    if (page > newLastPage) {
      // FIX ME: this is broken
      lastPage()
    }
    notify.success(
      stocksIdToDelete.length === 1
        ? '1 occurrence a été supprimée'
        : `${stocksIdToDelete.length} occurrences ont été supprimées`
    )
  }

  const onCancelClick = () => {
    setIsCheckedArray(stocks.map(() => false))
  }

  const selectedDateText =
    isCheckedArray.filter((e) => e === true).length > 1
      ? `${isCheckedArray.filter((e) => e === true).length} dates sélectionnées`
      : '1 date sélectionnée'

  const isAtLeastOneStockChecked = isCheckedArray.some((e) => e)
  const areFiltersActive = Boolean(
    dateFilter || timeFilter || priceCategoryIdFilter
  )

  return (
    <div className={className}>
      <div className={styles['select-all-container']}>
        {!readonly && (
          <BaseCheckbox
            label="Tout sélectionner"
            checked={areAllChecked || isAtLeastOneStockChecked}
            partialCheck={!areAllChecked && isAtLeastOneStockChecked}
            onChange={handleOnChangeSelectAll}
          />
        )}

        <div className={styles['stocks-count']}>
          {new Intl.NumberFormat('fr-FR').format(stocks.length)}{' '}
          {pluralizeString('occurrence', stocks.length)}
        </div>
      </div>

      <table className={styles['stock-event-table']}>
        <caption className="visually-hidden">
          Liste des dates et capacités
        </caption>

        <thead>
          <tr>
            <th
              scope="col"
              className={cn(styles['date-column'], styles['header'])}
            >
              <span className={styles['header-name']}>Date</span>

              <SortArrow
                onClick={() => onColumnHeaderClick(StocksOrderedBy.DATE)}
                sortingMode={
                  currentSortingColumn === StocksOrderedBy.DATE
                    ? currentSortingMode
                    : SortingMode.NONE
                }
              />

              <div className={cn(styles['filter-input'])}>
                <BaseDatePicker
                  onChange={(event) => {
                    setDateFilter(event.target.value)
                    onFilterChange()
                  }}
                  value={dateFilter}
                  filterVariant
                  aria-label="Filtrer par date"
                />
              </div>
            </th>

            <th
              scope="col"
              className={cn(styles['time-column'], styles['header'])}
            >
              <span className={styles['header-name']}>Horaire</span>

              <SortArrow
                onClick={() => onColumnHeaderClick(StocksOrderedBy.TIME)}
                sortingMode={
                  currentSortingColumn === StocksOrderedBy.TIME
                    ? currentSortingMode
                    : SortingMode.NONE
                }
              />
              <div className={cn(styles['filter-input'])}>
                <BaseTimePicker
                  onChange={(event) => {
                    setTimeFilter(event.target.value)
                    onFilterChange()
                  }}
                  value={timeFilter}
                  filterVariant
                  aria-label="Filtrer par horaire"
                />
              </div>
            </th>

            <th scope="col" className={styles['header']}>
              <span className={styles['header-name']}>Tarif</span>

              <SortArrow
                onClick={() =>
                  onColumnHeaderClick(StocksOrderedBy.PRICE_CATEGORY_ID)
                }
                sortingMode={
                  currentSortingColumn === StocksOrderedBy.PRICE_CATEGORY_ID
                    ? currentSortingMode
                    : SortingMode.NONE
                }
              />
              <div className={cn(styles['filter-input'])}>
                <SelectInput
                  name="priceCategoryFilter"
                  defaultOption={{ label: '', value: '' }}
                  options={priceCategoryOptions}
                  value={priceCategoryIdFilter}
                  onChange={(event) => {
                    setPriceCategoryIdFilter(event.target.value)
                    onFilterChange()
                  }}
                  filterVariant
                  aria-label="Filtrer par tarif"
                />
              </div>
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

              <SortArrow
                onClick={() =>
                  onColumnHeaderClick(StocksOrderedBy.BOOKING_LIMIT_DATETIME)
                }
                sortingMode={
                  currentSortingColumn ===
                  StocksOrderedBy.BOOKING_LIMIT_DATETIME
                    ? currentSortingMode
                    : SortingMode.NONE
                }
              />
              <div className={cn(styles['filter-input'])}>&nbsp;</div>
            </th>

            <th
              scope="col"
              className={cn(styles['quantity-column'], styles['header'])}
            >
              <span className={styles['header-name']}>Places</span>

              <SortArrow
                onClick={() =>
                  onColumnHeaderClick(StocksOrderedBy.REMAINING_QUANTITY)
                }
                sortingMode={
                  currentSortingColumn === StocksOrderedBy.REMAINING_QUANTITY
                    ? currentSortingMode
                    : SortingMode.NONE
                }
              />
              <div className={cn(styles['filter-input'])}>&nbsp;</div>
            </th>

            {readonly ? (
              <th
                className={cn(
                  styles['bookings-quantity-column'],
                  styles['header']
                )}
              >
                <span className={styles['header-name']}>Réservations</span>

                <SortArrow
                  onClick={() =>
                    onColumnHeaderClick(StocksOrderedBy.DN_BOOKED_QUANTITY)
                  }
                  sortingMode={
                    currentSortingColumn === StocksOrderedBy.DN_BOOKED_QUANTITY
                      ? currentSortingMode
                      : SortingMode.NONE
                  }
                />
                <div className={cn(styles['filter-input'])}>&nbsp;</div>
              </th>
            ) : (
              <th className={cn(styles['actions-column'], styles['header'])} />
            )}
          </tr>
        </thead>

        <tbody>
          {areFiltersActive && (
            <FilterResultsRow
              colSpan={6}
              onFiltersReset={() => {
                setDateFilter('')
                setTimeFilter('')
                setPriceCategoryIdFilter('')
                onFilterChange()
              }}
              resultsCount={stocks.length}
            />
          )}

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
              (pC) => pC.id === stock.priceCategoryId
            )

            let price = ''
            /* istanbul ignore next priceCategory would never be null */
            if (priceCategory) {
              price = `${formatPrice(
                priceCategory.price
              )} - ${priceCategory?.label}`
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
                    {!readonly && (
                      <BaseCheckbox
                        checked={isCheckedArray[currentStockIndex]}
                        onChange={() =>
                          handleOnChangeSelected(currentStockIndex)
                        }
                        label=""
                      />
                    )}

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

                {readonly ? (
                  <td className={styles['data']}>
                    {stock.bookingsQuantity ?? 0}
                  </td>
                ) : (
                  <td className={cn(styles['data'], styles['clear-icon'])}>
                    <Button
                      variant={ButtonVariant.TERNARY}
                      onClick={async () => {
                        if (stock.id?.toString()) {
                          await onDeleteStock(index, stock.id)
                        }
                      }}
                      icon={fullTrashIcon}
                      hasTooltip
                    >
                      Supprimer
                    </Button>
                  </td>
                )}
              </tr>
            )
          })}

          {stocks.length === 0 && <NoResultsRow colSpan={6} />}
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
