import { useState } from 'react'
import useSWR, { mutate } from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { GET_STOCKS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useNotification } from 'commons/hooks/useNotification'
import { pluralize } from 'commons/utils/pluralize'
import { Pagination } from 'ui-kit/Pagination/Pagination'

import { StocksTableFilters, StocksTableSort } from '../form/types'

import styles from './StocksCalendar.module.scss'
import { StocksCalendarActionsBar } from './StocksCalendarActionsBar/StocksCalendarActionsBar'
import { StocksCalendarFilters } from './StocksCalendarFilters/StocksCalendarFilters'
import { StocksCalendarLayout } from './StocksCalendarLayout/StocksCalendarLayout'
import { StocksCalendarTable } from './StocksCalendarTable/StocksCalendarTable'

const STOCKS_PER_PAGE = 20

export function StocksCalendar({
  offer,
  handlePreviousStep = () => {},
  handleNextStep = () => {},
  departmentCode,
  readonly = false,
}: {
  offer: GetIndividualOfferWithAddressResponseModel
  handlePreviousStep?: () => void
  handleNextStep?: () => void
  departmentCode: string
  readonly?: boolean
}) {
  const [page, setPage] = useState(1)
  const [checkedStocks, setCheckedStocks] = useState(new Set<number>())
  const [appliedFilters, setAppliedFilters] = useState<StocksTableFilters>({})
  const [appliedSort, setAppliedSort] = useState<StocksTableSort>({})
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
        filters.time || undefined,
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
  }

  const stocks = data?.stocks || []

  return (
    <StocksCalendarLayout
      offer={offer}
      isLoading={isLoading}
      readonly={readonly}
      hasStocks={Boolean(data?.hasStocks)}
      onAfterCloseDialog={async () => {
        await mutate(queryKeys, data, {
          revalidate: true,
        })
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
              readonly={readonly}
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
          handlePreviousStep={handlePreviousStep}
          handleNextStep={handleNextStep}
          checkedStocks={checkedStocks}
          hasStocks={Boolean(data?.hasStocks)}
          deleteStocks={deleteStocks}
          updateCheckedStocks={setCheckedStocks}
          readonly={readonly}
        />
      </div>
    </StocksCalendarLayout>
  )
}
