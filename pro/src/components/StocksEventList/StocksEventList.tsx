import cn from 'classnames'
import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  GetStocksResponseModel,
  PriceCategoryResponseModel,
  StocksOrderedBy,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { SortingMode, useColumnSorting } from 'commons/hooks/useColumnSorting'
import { useNotification } from 'commons/hooks/useNotification'
import { usePaginationWithSearchParams } from 'commons/hooks/usePagination'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { formatPrice } from 'commons/utils/formatPrice'
import { pluralize, pluralizeString } from 'commons/utils/pluralize'
import {
  convertTimeFromVenueTimezoneToUtc,
  formatLocalTimeDateString,
  isValidTime,
} from 'commons/utils/timezone'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { AddRecurrencesButton } from 'components/IndividualOffer/StocksEventCreation/AddRecurrencesButton'
import { getPriceCategoryOptions } from 'components/IndividualOffer/StocksEventEdition/getPriceCategoryOptions'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import fullRefreshIcon from 'icons/full-refresh.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { serializeStockEvents } from 'pages/IndividualOfferWizard/Stocks/serializeStockEvents'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { Select } from 'ui-kit/form/Select/Select'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { Spinner } from 'ui-kit/Spinner/Spinner'

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
  priceCategories: PriceCategoryResponseModel[]
  departmentCode?: string | null
  offer: GetIndividualOfferWithAddressResponseModel
  readonly?: boolean
  onStocksLoad?: (hasStocks: boolean) => void
  canAddStocks?: boolean
}

enum PartialCheck {
  CHECKED = 'checked',
  PARTIAL = 'partial',
  UNCHECKED = 'unchecked',
}

const DELETE_STOCKS_CHUNK_SIZE = 50

function* chunks<T>(array: T[], n: number): Generator<T[], void> {
  for (let i = 0; i < array.length; i += n) {
    yield array.slice(i, i + n)
  }
}

export const StocksEventList = ({
  priceCategories,
  departmentCode,
  offer,
  readonly = false,
  onStocksLoad,
  canAddStocks = false,
}: StocksEventListProps) => {
  // utilities
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const [searchParams, setSearchParams] = useSearchParams()
  const { mutate } = useSWRConfig()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  // states
  const [allStocksChecked, setAllStocksChecked] = useState<PartialCheck>(
    PartialCheck.UNCHECKED
  )
  const [checkedStocks, setCheckedStocks] = useState<boolean[]>([])
  const [stocks, setStocks] = useState<StocksEvent[]>([])
  const [offerHasStocks, setOfferHasStocks] = useState<boolean | null>(null)
  const [stocksCountWithFilters, setStocksCountWithFilters] =
    useState<number>(0)
  const [isDeleteAllLoading, setIsDeleteAllLoading] = useState(false)
  const [dateFilter, setDateFilter] = useState(searchParams.get('date'))
  const [timeFilter, setTimeFilter] = useState<string>(
    searchParams.get('time') || ''
  )
  const [priceCategoryIdFilter, setPriceCategoryIdFilter] = useState(
    searchParams.get('priceCategoryId')
  )
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<StocksOrderedBy>()
  const { page, previousPage, nextPage, pageCount, firstPage } =
    usePaginationWithSearchParams(STOCKS_PER_PAGE, stocksCountWithFilters)

  function sortTableColumn(col: StocksOrderedBy) {
    logEvent(Events.CLICKED_SORT_STOCKS_TABLE, {
      formType: readonly ? 'readonly' : 'creation',
      sortBy: col,
      offerId: offer.id,
      venueId: offer.venue.id,
    })
    onColumnHeaderClick(col)
  }

  // Effects
  const loadStocksFromCurrentFilters = () =>
    api.getStocks(
      offer.id,
      dateFilter ? dateFilter : undefined,
      isValidTime(timeFilter)
        ? convertTimeFromVenueTimezoneToUtc(timeFilter, departmentCode)
        : undefined,
      priceCategoryIdFilter ? Number(priceCategoryIdFilter) : undefined,
      currentSortingColumn ?? undefined,
      currentSortingMode === SortingMode.DESC,
      Number(page || 1)
    )

  const handleStocksResponse = (response: GetStocksResponseModel) => {
    setStocks(serializeStockEvents(response.stocks))
    setOfferHasStocks(response.hasStocks)
    setStocksCountWithFilters(response.stockCount)
    if (onStocksLoad) {
      onStocksLoad(response.hasStocks)
    }
  }

  const reloadStocks = async () => {
    const response = await loadStocksFromCurrentFilters()
    handleStocksResponse(response)
  }

  useEffect(() => {
    if (dateFilter) {
      searchParams.set('date', dateFilter)
    } else {
      searchParams.delete('date')
    }
    if (timeFilter) {
      searchParams.set('time', timeFilter)
    } else {
      searchParams.delete('time')
    }
    if (priceCategoryIdFilter) {
      searchParams.set('priceCategoryId', priceCategoryIdFilter)
    } else {
      searchParams.delete('priceCategoryId')
    }
    if (currentSortingColumn) {
      searchParams.set('orderBy', currentSortingColumn)
    } else {
      searchParams.delete('orderBy')
    }
    if (currentSortingMode === SortingMode.DESC) {
      searchParams.set('orderByDesc', '1')
    } else if (currentSortingMode === SortingMode.ASC) {
      searchParams.set('orderByDesc', '0')
    } else {
      searchParams.delete('orderByDesc')
    }

    setSearchParams(searchParams)

    async function loadStocks() {
      const response = await loadStocksFromCurrentFilters()

      if (!ignore) {
        handleStocksResponse(response)
        setCheckedStocks(response.stocks.map(() => false))
        setAllStocksChecked(PartialCheck.UNCHECKED)
      }
    }

    // we set ignore variable to avoid race conditions
    // see react doc:  https://react.dev/reference/react/useEffect#fetching-data-with-effects
    let ignore = false

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStocks()
    return () => {
      ignore = true
    }
  }, [
    dateFilter,
    timeFilter,
    priceCategoryIdFilter,
    currentSortingColumn,
    currentSortingMode,
    page,
  ])

  // Derived data
  const priceCategoryOptions = getPriceCategoryOptions(priceCategories)
  const selectedDateText =
    allStocksChecked === PartialCheck.CHECKED
      ? pluralize(stocksCountWithFilters, 'dates sélectionnées')
      : pluralize(
          checkedStocks.filter((stock) => stock).length,
          'dates sélectionnées'
        )
  const isAtLeastOneStockChecked = checkedStocks.some((e) => e)
  const areFiltersActive = Boolean(
    dateFilter || timeFilter || priceCategoryIdFilter
  )

  // Handlers
  const onFilterChange = () => {
    firstPage()
    logEvent(Events.UPDATED_EVENT_STOCK_FILTERS, {
      formType: readonly ? 'readonly' : 'creation',
    })
  }

  const onStockCheckChange = (index: number) => {
    const newArray = checkedStocks.map((isChecked) => isChecked)
    newArray[index] = !newArray[index]
    setCheckedStocks(newArray)
    setAllStocksChecked(
      newArray.some((check) => check)
        ? PartialCheck.PARTIAL
        : PartialCheck.UNCHECKED
    )
  }

  const onAllStocksCheckChange = () => {
    if (allStocksChecked === PartialCheck.CHECKED) {
      setAllStocksChecked(PartialCheck.UNCHECKED)
      setCheckedStocks(stocks.map(() => false))
    } else {
      setAllStocksChecked(PartialCheck.CHECKED)
      setCheckedStocks(stocks.map(() => true))
    }
  }

  const onDeleteStock = async (selectIndex: number, stockId: number) => {
    await api.deleteStock(stockId)
    logEvent(Events.CLICKED_DELETE_STOCK, {
      offererId: selectedOffererId?.toString(),
      offerId: offer.id,
      offerType: 'individual',
      stockId: stockId,
    })

    // If it was the last stock of the page, go to previous page
    if (stocks.length === 1 && page > 1) {
      previousPage()
    } else {
      await reloadStocks()

      // handle checkbox selection
      const newArray = [...checkedStocks]
      newArray.splice(selectIndex, 1)
      setCheckedStocks(newArray)
    }

    // When all stocks are deleted, we need to reload the offer
    // to disable the stepper
    if (stocks.length === 1 && page === 1) {
      await mutate([GET_OFFER_QUERY_KEY, offer.id])
    }
    notify.success('1 date a été supprimée')
  }

  const onBulkDelete = async () => {
    setIsDeleteAllLoading(true)
    const stocksIdToDelete = stocks
      .filter((stock, index) => checkedStocks[index])
      .map((stock) => stock.id)
    const deletionCount =
      allStocksChecked === PartialCheck.CHECKED
        ? stocksCountWithFilters
        : stocksIdToDelete.length

    // If all stocks are checked without any stock unchecked,
    // use the delete all route with filters
    if (allStocksChecked === PartialCheck.CHECKED) {
      await api.deleteAllFilteredStocks(offer.id, {
        date: dateFilter ? dateFilter : undefined,
        time: timeFilter
          ? convertTimeFromVenueTimezoneToUtc(timeFilter, departmentCode)
          : undefined,
        price_category_id:
          priceCategoryIdFilter === null
            ? null
            : parseInt(priceCategoryIdFilter),
      })
      // We don't know how many stocks are left after the deletion,
      // so we reload the first page
      if (page !== 1) {
        firstPage()
      } else {
        await reloadStocks()
      }
    } else {
      // Otherwise, use the bulk delete stocks by id route
      if (stocksIdToDelete.length > 0) {
        await Promise.all(
          [...chunks(stocksIdToDelete, DELETE_STOCKS_CHUNK_SIZE)].map((ids) =>
            api.deleteStocks(offer.id, { ids_to_delete: ids })
          )
        )
        // If it was the last stock of the page, go to previous page
        if (stocks.length === stocksIdToDelete.length && page > 1) {
          previousPage()
        } else {
          await reloadStocks()
        }
      }
    }

    setCheckedStocks(stocks.map(() => false))
    setAllStocksChecked(PartialCheck.UNCHECKED)
    setIsDeleteAllLoading(false)
    logEvent(Events.CLICKED_BULK_DELETE_STOCK, {
      offererId: selectedOffererId?.toString(),
      offerId: offer.id,
      offerType: 'individual',
      deletionCount: deletionCount,
    })

    // When all stocks are deleted, we need to reload the offer
    // to disable the stepper
    await mutate([GET_OFFER_QUERY_KEY, offer.id])
    notify.success(
      stocksIdToDelete.length === 1
        ? '1 date a été supprimée'
        : `${new Intl.NumberFormat('fr-FR').format(
            stocksIdToDelete.length
          )} dates ont été supprimées`
    )
  }

  const onCancelClick = () => {
    setCheckedStocks(stocks.map(() => false))
    setAllStocksChecked(PartialCheck.UNCHECKED)
  }

  if (offerHasStocks === null) {
    return <Spinner />
  }

  return (
    <div className={styles['recurrences-container']}>
      {canAddStocks && (
        <div className={styles['recurrences-button']}>
          <AddRecurrencesButton offer={offer} reloadStocks={reloadStocks} />
        </div>
      )}

      {(!canAddStocks || offerHasStocks) && (
        <>
          <div className={cn(styles['filter-input'])}>
            <div>
              <DatePicker
                name={'dateFilter'}
                label="Filtrer par date"
                onChange={(event) => {
                  setDateFilter(event.target.value)
                  onFilterChange()
                }}
                value={dateFilter ?? ''}
              />
            </div>
            <div>
              <TimePicker
                name={'timeFilter'}
                label="Filtrer par horaire"
                onChange={(event) => {
                  setTimeFilter(event.target.value)
                  onFilterChange()
                }}
                value={timeFilter}
              />
            </div>
            <div>
              <Select
                name="priceCategoryFilter"
                label="Filtrer par tarif"
                defaultOption={{ label: '', value: '' }}
                options={priceCategoryOptions}
                value={priceCategoryIdFilter ?? ''}
                onChange={(event) => {
                  setPriceCategoryIdFilter(event.target.value)
                  onFilterChange()
                }}
              />
            </div>
          </div>
          <Button
            icon={fullRefreshIcon}
            variant={ButtonVariant.TERNARY}
            onClick={() => {
              setDateFilter('')
              setTimeFilter('')
              setPriceCategoryIdFilter('')
              onFilterChange()
            }}
            disabled={!areFiltersActive}
          >
            Réinitialiser les filtres
          </Button>

          <div className={styles['select-all-container']}>
            {!readonly && (
              <Checkbox
                label="Tout sélectionner"
                checked={allStocksChecked !== PartialCheck.UNCHECKED}
                indeterminate={allStocksChecked === PartialCheck.PARTIAL}
                onChange={onAllStocksCheckChange}
              />
            )}

            <div>
              {new Intl.NumberFormat('fr-FR').format(stocksCountWithFilters)}{' '}
              {pluralizeString('date', stocksCountWithFilters)}
            </div>
          </div>

          <table className={styles['stock-event-table']}>
            <caption className={styles['visually-hidden']}>
              Liste des dates et capacités
            </caption>

            <thead>
              <tr className={styles['row-head']}>
                <th
                  scope="col"
                  className={cn(styles['date-column'], styles['header'])}
                  colSpan={2}
                  onClick={() => sortTableColumn(StocksOrderedBy.DATE)}
                >
                  <span className={styles['header-name']}>Date</span>

                  <SortArrow
                    onClick={() => sortTableColumn(StocksOrderedBy.DATE)}
                    sortingMode={
                      currentSortingColumn === StocksOrderedBy.DATE
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                </th>

                <th
                  scope="col"
                  className={cn(styles['time-column'], styles['header'])}
                  onClick={() => sortTableColumn(StocksOrderedBy.TIME)}
                >
                  <span className={styles['header-name']}>Horaire</span>

                  <SortArrow
                    onClick={() => sortTableColumn(StocksOrderedBy.TIME)}
                    sortingMode={
                      currentSortingColumn === StocksOrderedBy.TIME
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                </th>

                <th
                  scope="col"
                  className={cn(styles['price-column'], styles['header'])}
                  onClick={() =>
                    sortTableColumn(StocksOrderedBy.PRICE_CATEGORY_ID)
                  }
                >
                  <span className={styles['header-name']}>Tarif</span>

                  <SortArrow
                    onClick={() =>
                      sortTableColumn(StocksOrderedBy.PRICE_CATEGORY_ID)
                    }
                    sortingMode={
                      currentSortingColumn === StocksOrderedBy.PRICE_CATEGORY_ID
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                </th>

                <th
                  scope="col"
                  className={cn(
                    styles['booking-limit-date-column'],
                    styles['header']
                  )}
                  onClick={() =>
                    sortTableColumn(StocksOrderedBy.BOOKING_LIMIT_DATETIME)
                  }
                >
                  <span className={styles['header-name']}>
                    Date limite de réservation
                  </span>

                  <SortArrow
                    onClick={() =>
                      sortTableColumn(StocksOrderedBy.BOOKING_LIMIT_DATETIME)
                    }
                    sortingMode={
                      currentSortingColumn ===
                      StocksOrderedBy.BOOKING_LIMIT_DATETIME
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                </th>

                <th
                  scope="col"
                  className={cn(styles['quantity-column'], styles['header'])}
                  onClick={() =>
                    sortTableColumn(StocksOrderedBy.REMAINING_QUANTITY)
                  }
                >
                  <span className={styles['header-name']}>Places</span>

                  <SortArrow
                    onClick={() =>
                      sortTableColumn(StocksOrderedBy.REMAINING_QUANTITY)
                    }
                    sortingMode={
                      currentSortingColumn ===
                      StocksOrderedBy.REMAINING_QUANTITY
                        ? currentSortingMode
                        : SortingMode.NONE
                    }
                  />
                </th>

                {readonly ? (
                  <th
                    className={cn(
                      styles['bookings-quantity-column'],
                      styles['header']
                    )}
                    onClick={() =>
                      sortTableColumn(StocksOrderedBy.DN_BOOKED_QUANTITY)
                    }
                  >
                    <span className={styles['header-name']}>Réservations</span>

                    <SortArrow
                      onClick={() =>
                        sortTableColumn(StocksOrderedBy.DN_BOOKED_QUANTITY)
                      }
                      sortingMode={
                        currentSortingColumn ===
                        StocksOrderedBy.DN_BOOKED_QUANTITY
                          ? currentSortingMode
                          : SortingMode.NONE
                      }
                    />
                  </th>
                ) : (
                  <th
                    className={cn(styles['actions-column'], styles['header'])}
                  />
                )}
              </tr>
            </thead>

            <tbody className={styles['body']}>
              {stocks.map((stock) => {
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
                  )} - ${priceCategory.label}`
                }

                const stockIndex = stocks.findIndex((s) => s.id === stock.id)
                return (
                  <tr key={stock.id} className={styles['row']}>
                    <td
                      className={cn(styles['data'], styles['checkbox-column'])}
                      data-label="Sélection du stock"
                    >
                      {!readonly && (
                        <Checkbox
                          checked={checkedStocks[stockIndex]}
                          onChange={() => onStockCheckChange(stockIndex)}
                          label={beginningDay}
                        />
                      )}
                    </td>
                    <td
                      className={cn(styles['data'], styles['date-column'])}
                      data-label="Date"
                    >
                      <div
                        className={cn(
                          styles['date-cell-wrapper'],
                          styles['capitalize']
                        )}
                      >
                        {readonly && (
                          <div className={styles['day']}>
                            <strong>{beginningDay}</strong>
                          </div>
                        )}
                        <div>{beginningDate}</div>
                      </div>
                    </td>

                    <td className={styles['data']} data-label="Horaire">
                      {beginningHour}
                    </td>

                    <td className={styles['data']} data-label="Tarif">
                      {price}
                    </td>

                    <td className={styles['data']} data-label="Date limite">
                      {bookingLimitDate}
                    </td>

                    <td className={styles['data']} data-label="Places">
                      {stock.quantity === null
                        ? 'Illimité'
                        : new Intl.NumberFormat('fr-FR').format(stock.quantity)}
                    </td>

                    {readonly ? (
                      <td className={styles['data']} data-label="Réservations">
                        {stock.bookingsQuantity}
                      </td>
                    ) : (
                      <td
                        className={cn(styles['data'], styles['clear-icon'])}
                        data-label="Supprimer"
                      >
                        <Button
                          variant={ButtonVariant.TERNARY}
                          onClick={async () => {
                            if (stock.id.toString()) {
                              await onDeleteStock(stockIndex, stock.id)
                            }
                          }}
                          icon={fullTrashIcon}
                          tooltipContent={<>Supprimer</>}
                        />
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
        </>
      )}
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
                <Button onClick={onBulkDelete} isLoading={isDeleteAllLoading}>
                  Supprimer ces dates
                </Button>
              </>
            }
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      )}
    </div>
  )
}
