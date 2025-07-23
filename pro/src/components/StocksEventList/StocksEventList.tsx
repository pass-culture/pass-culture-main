import { useState } from 'react'
import { useSelector } from 'react-redux'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  PriceCategoryResponseModel,
  StocksOrderedBy,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_OFFER_QUERY_KEY,
  GET_STOCKS_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { usePaginationWithSearchParams } from 'commons/hooks/usePagination'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { formatPrice } from 'commons/utils/formatPrice'
import { pluralize, pluralizeString } from 'commons/utils/pluralize'
import {
  convertTimeFromVenueTimezoneToUtc,
  formatLocalTimeDateString,
} from 'commons/utils/timezone'
import { AddRecurrencesButton } from 'components/IndividualOffer/StocksEventCreation/AddRecurrencesButton'
import {
  StocksTableFilters,
  StocksTableSort,
} from 'components/IndividualOffer/StocksEventCreation/form/types'
import { StocksCalendarActionsBar } from 'components/IndividualOffer/StocksEventCreation/StocksCalendar/StocksCalendarActionsBar/StocksCalendarActionsBar'
import { StocksCalendarFilters } from 'components/IndividualOffer/StocksEventCreation/StocksCalendar/StocksCalendarFilters/StocksCalendarFilters'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
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
  canAddStocks = false,
}: StocksEventListProps) => {
  // utilities
  const { logEvent } = useAnalytics()
  //const notify = useNotification()
  // const [searchParams, setSearchParams] = useSearchParams()
  const { mutate } = useSWRConfig()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  // states
  // const [checkedStocks, setCheckedStocks] = useState<boolean[]>([])
  // const [stocks, setStocks] = useState<StocksEvent[]>([])
  // const [offerHasStocks, setOfferHasStocks] = useState<boolean | null>(null)
  // const [stocksCountWithFilters, setStocksCountWithFilters] =
  //   useState<number>(0)
  const [isDeleteAllLoading, setIsDeleteAllLoading] = useState(false)

  // const [dateFilter, setDateFilter] = useState(searchParams.get('date'))
  // const [timeFilter, setTimeFilter] = useState<string>(
  //   searchParams.get('time') || ''
  // )
  // const [priceCategoryIdFilter, setPriceCategoryIdFilter] = useState(
  //   searchParams.get('priceCategoryId')
  // )
  // const { currentSortingColumn, currentSortingMode } =
  //   useColumnSorting<StocksOrderedBy>()

  const { previousPage, nextPage, pageCount, firstPage } =
    usePaginationWithSearchParams(STOCKS_PER_PAGE)

  const [page, setPage] = useState(1)
  const [checkedStocks, setCheckedStocks] = useState(new Set<number>())
  const [appliedFilters, setAppliedFilters] = useState<StocksTableFilters>({})
  const [appliedSort, setAppliedSort] = useState<StocksTableSort>({
    sort: StocksOrderedBy.DATE,
  })
  const notify = useNotification()

  const queryKeys: [
    string,
    number,
    number,
    StocksTableFilters,
    StocksTableSort,
  ] = [GET_STOCKS_QUERY_KEY, offer.id, page, appliedFilters, appliedSort]

  const { data, isLoading } = useSWR(
    queryKeys,
    ([, offerId, pageNum, filters, sortType]) =>
      api.getStocks(
        offerId,
        filters.date || undefined,
        filters.time
          ? convertTimeFromVenueTimezoneToUtc(filters.time, departmentCode)
          : undefined,
        filters.priceCategoryId ? Number(filters.priceCategoryId) : undefined,
        sortType.sort,
        sortType.orderByDesc,
        pageNum || 1,
        STOCKS_PER_PAGE
      ),
    {
      //  Display previous data in the table until the new data has loaded so that
      //  the scroll position in the table remains the same in-between pagination loads
      keepPreviousData: true,
      onSuccess: () => {
        setCheckedStocks(new Set())
      },
    }
  )

  console.log(data)

  async function onDeleteStock(ids: number[]) {
    await api.deleteStocks(offer.id, { ids_to_delete: ids })

    if (
      page > 1 &&
      data?.stockCount &&
      data.stockCount - ids.length <= (page - 1) * STOCKS_PER_PAGE
    ) {
      //  Descrease the page number if deleting the ids would leave the user on an empty stocks page
      setPage((p) => p - 1)
    }

    notify.success(pluralize(ids.length, 'date a été supprimée'))

    await mutate(queryKeys)
    await mutate([GET_OFFER_QUERY_KEY, offer.id])
  }

  const stocks = data?.stocks || []

  const columns = [
    {
      label: 'Date',
      id: 'beginningDatetime',
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
      render: (stock: { quantity: number | null }) =>
        stock.quantity === null
          ? 'Illimité'
          : new Intl.NumberFormat('fr-FR').format(stock.quantity),
    },
    readonly && {
      label: 'Réservations',
      id: 'bookingsQuantity',
      render: (stock: { bookingsQuantity: number | string }) =>
        stock.bookingsQuantity,
    },
    !readonly && {
      label: '',
      id: 'deleteAction',
      render: (stock: { id: number }) => (
        <Button
          variant={ButtonVariant.TERNARY}
          onClick={() => onDeleteStock([stock.id])}
          icon={fullTrashIcon}
          tooltipContent="Supprimer"
        />
      ),
    },
  ].filter(Boolean)

  return (
    <div className={styles['recurrences-container']}>
      {canAddStocks && (
        <div className={styles['recurrences-button']}>
          <AddRecurrencesButton
            offer={offer}
            reloadStocks={async () => {
              await mutate(queryKeys, data, {
                revalidate: true,
              })
              await mutate([GET_OFFER_QUERY_KEY, offer.id])
            }}
          />
        </div>
      )}

      {(!canAddStocks || data?.hasStocks) && (
        <>
          <StocksCalendarFilters
            priceCategories={offer.priceCategories}
            filters={appliedFilters}
            sortType={appliedSort}
            onUpdateFilters={setAppliedFilters}
            onUpdateSort={(sort, desc) => {
              setAppliedSort({
                sort: sort ? sort : undefined,
                orderByDesc: Boolean(desc),
              })
            }}
            mode={OFFER_WIZARD_MODE.CREATION}
          />

          <div className={styles['table-wrapper']}>
            <Table
              columns={columns}
              data={stocks}
              isLoading={isLoading}
              variant={TableVariant.COLLAPSE}
              selectable={!readonly}
              selectedNumber={`${new Intl.NumberFormat('fr-FR').format(stocks.length)} ${' '}
            ${pluralizeString('date', stocks.length)}`}
              selectedIds={checkedStocks}
              onSelectionChange={setCheckedStocks}
              noResult={{
                resetFilter: setAppliedFilters,
                message: 'Aucune date trouvée',
              }}
            />
          </div>
          <div className={styles['pagination']}>
            <Pagination
              currentPage={page}
              onNextPageClick={() => setPage((p) => p + 1)}
              onPreviousPageClick={() => setPage((p) => p - 1)}
              pageCount={
                data.stockCount % STOCKS_PER_PAGE === 0
                  ? data.stockCount / STOCKS_PER_PAGE
                  : Math.trunc(data.stockCount / STOCKS_PER_PAGE) + 1
              }
            />
          </div>
        </>
      )}

      <StocksCalendarActionsBar
        checkedStocks={checkedStocks}
        hasStocks={Boolean(data?.hasStocks)}
        deleteStocks={onDeleteStock}
        updateCheckedStocks={setCheckedStocks}
        mode={OFFER_WIZARD_MODE.CREATION}
        offerId={offer.id}
      />
    </div>
  )
}
