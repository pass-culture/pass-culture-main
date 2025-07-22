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
import fullRefreshIcon from 'icons/full-refresh.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { serializeStockEvents } from 'pages/IndividualOfferWizard/Stocks/serializeStockEvents'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { Select } from 'ui-kit/form/Select/Select'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { Table, TableVariant } from 'ui-kit/Table/Table'

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
  const { currentSortingColumn, currentSortingMode } =
    useColumnSorting<StocksOrderedBy>()

  const { page, previousPage, nextPage, pageCount, firstPage } =
    usePaginationWithSearchParams(STOCKS_PER_PAGE, stocksCountWithFilters)

  const areAllSelected = checkedStocks.length === stocks.length

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

    setSearchParams(searchParams)

    async function loadStocks() {
      const response = await loadStocksFromCurrentFilters()

      if (!ignore) {
        handleStocksResponse(response)
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
      .filter((_stock, index) => checkedStocks[index])
      .map((stock) => stock.id)

    if (areAllSelected) {
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

      notify.success(
        `${new Intl.NumberFormat('fr-FR').format(
          stocksCountWithFilters
        )} dates ont été supprimées`
      )
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

        notify.success(
          pluralize(stocksIdToDelete.length, 'date a été supprimée')
        )
      }
    }

    setCheckedStocks([])
    setIsDeleteAllLoading(false)
    logEvent(Events.CLICKED_BULK_DELETE_STOCK, {
      offererId: selectedOffererId?.toString(),
      offerId: offer.id,
      offerType: 'individual',
      deletionCount: checkedStocks.length,
    })

    // When all stocks are deleted, we need to reload the offer
    // to disable the stepper
    await mutate([GET_OFFER_QUERY_KEY, offer.id])
  }

  const onCancelClick = () => {
    setCheckedStocks([])
  }

  const columns = [
    {
      label: 'Date',
      id: 'beginningDatetime',
      ordererField: 'beginningDatetime',
      sortable: true,
      render: (stock: { beginningDatetime: string | number | Date }) => {
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

        return (
          <div className={styles['date-cell-wrapper']}>
            <div className={styles['day']}>
              <strong>{beginningDay}</strong>
            </div>
            <div>{beginningDate}</div>
          </div>
        )
      },
    },
    {
      label: 'Horaire',
      id: 'beginningDatetime',
      sortable: true,
      ordererField: 'beginningDatetime',
      render: (stock: { beginningDatetime: string | number | Date }) =>
        formatLocalTimeDateString(
          stock.beginningDatetime,
          departmentCode,
          'HH:mm'
        ),
    },
    {
      label: 'Tarif',
      id: 'priceCategoryId',
      sortable: true,
      ordererField: 'priceCategoryId',
      render: (stock: { priceCategoryId: number }) => {
        const category = priceCategories.find(
          (p) => p.id === stock.priceCategoryId
        )
        return category
          ? `${formatPrice(category.price)} - ${category.label}`
          : ''
      },
    },
    {
      label: 'Date limite de réservation',
      id: 'bookingLimitDatetime',
      sortable: true,
      ordererField: 'bookingLimitDatetime',
      render: (stock: { bookingLimitDatetime: string | number | Date }) =>
        formatLocalTimeDateString(
          stock.bookingLimitDatetime,
          departmentCode,
          'dd/MM/yyyy'
        ),
    },
    {
      label: 'Places',
      id: 'quantity',
      sortable: true,
      ordererField: 'quantity',
      render: (stock: { quantity: number | null }) =>
        stock.quantity === null
          ? 'Illimité'
          : new Intl.NumberFormat('fr-FR').format(stock.quantity),
    },
    readonly && {
      label: 'Réservations',
      id: 'bookingsQuantity',
      sortable: true,
      ordererField: 'bookingsQuantity',
      render: (stock: { bookingsQuantity: number | string }) =>
        stock.bookingsQuantity,
    },
    !readonly && {
      label: '',
      id: 'deleteAction',
      render: (stock: { id: number }, index: number) => (
        <Button
          variant={ButtonVariant.TERNARY}
          onClick={() => onDeleteStock(index, stock.id)}
          icon={fullTrashIcon}
          tooltipContent="Supprimer"
        />
      ),
    },
  ].filter(Boolean)

  const onResetFilter = () => {
    setDateFilter('')
    setTimeFilter('')
    setPriceCategoryIdFilter('')
    onFilterChange()
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
            onClick={onResetFilter}
            disabled={!areFiltersActive}
          >
            Réinitialiser les filtres
          </Button>

          <div className={styles['table-wrapper']}>
            <Table
              columns={columns}
              data={stocks}
              isLoading={offerHasStocks === null}
              variant={TableVariant.COLLAPSE}
              selectable={!readonly}
              selectedNumber={`${new Intl.NumberFormat('fr-FR').format(stocksCountWithFilters)} ${' '}
            ${pluralizeString('date', stocksCountWithFilters)}`}
              selectedIds={checkedStocks}
              onSelectionChange={(rows) => {
                setCheckedStocks(rows.map((r) => r.id))
              }}
              noResult={{
                resetFilter: onResetFilter,
                message: 'Aucune date trouvée',
              }}
            />
          </div>
          <Pagination
            currentPage={page}
            pageCount={pageCount}
            onPreviousPageClick={previousPage}
            onNextPageClick={nextPage}
          />
        </>
      )}

      {checkedStocks.length > 0 && (
        <ActionsBarSticky className={styles['actions']}>
          <ActionsBarSticky.Left>
            {areAllSelected
              ? pluralize(stocksCountWithFilters, 'dates sélectionnées')
              : pluralize(checkedStocks.length, 'dates sélectionnées')}
          </ActionsBarSticky.Left>
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
