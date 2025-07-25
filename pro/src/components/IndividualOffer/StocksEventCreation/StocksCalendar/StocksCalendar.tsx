import { useState } from 'react'
import useSWR, { mutate } from 'swr'

import { api } from 'apiClient/api'
import {
  EventStockUpdateBodyModel,
  GetIndividualOfferWithAddressResponseModel,
  StocksOrderedBy,
} from 'apiClient/v1'
import {
  GET_OFFER_QUERY_KEY,
  GET_STOCKS_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { getDepartmentCode } from 'commons/utils/getDepartmentCode'
import { pluralize } from 'commons/utils/pluralize'
import { convertTimeFromVenueTimezoneToUtc } from 'commons/utils/timezone'
import { Pagination } from 'ui-kit/Pagination/Pagination'

import { StocksTableFilters, StocksTableSort } from '../form/types'

import styles from './StocksCalendar.module.scss'
import { StocksCalendarActionsBar } from './StocksCalendarActionsBar/StocksCalendarActionsBar'
import { StocksCalendarFilters } from './StocksCalendarFilters/StocksCalendarFilters'
import { StocksCalendarLayout } from './StocksCalendarLayout/StocksCalendarLayout'
import { StocksCalendarTable } from './StocksCalendarTable/StocksCalendarTable'

const STOCKS_PER_PAGE = 20

export type StocksCalendarProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
}

export function StocksCalendar({ offer, mode }: StocksCalendarProps) {
  const [page, setPage] = useState(1)
  const [checkedStocks, setCheckedStocks] = useState(new Set<number>())
  const [appliedFilters, setAppliedFilters] = useState<StocksTableFilters>({})
  const [appliedSort, setAppliedSort] = useState<StocksTableSort>({
    sort: StocksOrderedBy.DATE,
  })
  const notify = useNotification()

  const departmentCode = getDepartmentCode(offer)

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

  async function deleteStocks(ids: number[]) {
    await api.deleteStocks(offer.id, { ids_to_delete: ids })

    if (
      page > 1 &&
      data?.stockCount &&
      data.stockCount - ids.length <= (page - 1) * STOCKS_PER_PAGE
    ) {
      //  Descrease the page number if deleting the ids would leave the user on an empty stocks page
      setPage((p) => p - 1)
    }

    notify.success(
      ids.length === 1
        ? 'Une date a été supprimée'
        : `${ids.length} dates ont été supprimées`
    )
    await mutate(queryKeys)
    await mutate([GET_OFFER_QUERY_KEY, offer.id])
  }

  async function updateStock(stock: EventStockUpdateBodyModel) {
    await api.bulkUpdateEventStocks({
      offerId: offer.id,
      stocks: [stock],
    })

    notify.success('Les modifications ont été enregistrées')

    await mutate(queryKeys)
  }

  const stocks = data?.stocks || []

  return (
    <StocksCalendarLayout
      offer={offer}
      isLoading={isLoading}
      mode={mode}
      hasStocks={Boolean(data?.hasStocks)}
      onAfterCloseDialog={async () => {
        await mutate(queryKeys, data, {
          revalidate: true,
        })
        await mutate([GET_OFFER_QUERY_KEY, offer.id])
      }}
    >
      <div className={styles['container']}>
        {data?.hasStocks && (
          <div className={styles['content']}>
            <div className={styles['filters']}>
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
                mode={mode}
              />
            </div>
            {data.stockCount > 0 && (
              <div className={styles['count']}>
                {pluralize(data.stockCount, 'date')}
              </div>
            )}
            <StocksCalendarTable
              stocks={stocks}
              offer={offer}
              onDeleteStocks={deleteStocks}
              checkedStocks={checkedStocks}
              updateCheckedStocks={setCheckedStocks}
              departmentCode={departmentCode}
              mode={mode}
              onUpdateStock={updateStock}
            />
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
          </div>
        )}

        <StocksCalendarActionsBar
          checkedStocks={checkedStocks}
          hasStocks={Boolean(data?.hasStocks)}
          deleteStocks={deleteStocks}
          updateCheckedStocks={setCheckedStocks}
          mode={mode}
          offerId={offer.id}
        />
      </div>
    </StocksCalendarLayout>
  )
}
