import React from 'react'
import {
  Column,
  useExpanded,
  usePagination,
  useSortBy,
  useTable,
} from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared'
import useAnalytics from 'hooks/useAnalytics'
import { Pagination } from 'ui-kit/Pagination'

import TableBody from '../Body'
import TableHead from '../Head'

import styles from './TableWrapper.module.scss'

interface TableWrapperProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  columns: Column<T>[]
  currentPage: number
  data: T[]
  nbBookings: number
  nbBookingsPerPage: number
  updateCurrentPage: (pageNumber: number) => void
  audience: Audience
  reloadBookings: () => void
  bookingId: string
}

const TableWrapper = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  columns,
  currentPage,
  data,
  nbBookings,
  nbBookingsPerPage,
  updateCurrentPage,
  audience,
  reloadBookings,
  bookingId,
}: TableWrapperProps<T>): JSX.Element => {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    nextPage,
    previousPage,
    prepareRow,
    page,
    state: { pageIndex },
  } = useTable(
    {
      columns,
      data,
      initialState: {
        pageIndex: currentPage,
        pageSize: nbBookingsPerPage,
      },
    },
    useSortBy,
    useExpanded,
    usePagination
  )
  const { logEvent } = useAnalytics()

  const pageCount = Math.ceil(nbBookings / nbBookingsPerPage)

  const goToNextPage = () => {
    nextPage()
    updateCurrentPage(pageIndex + 1)
    logEvent?.(Events.CLICKED_PAGINATION_NEXT_PAGE, {
      from: location.pathname,
    })
  }

  const goToPreviousPage = () => {
    previousPage()
    updateCurrentPage(pageIndex - 1)
    logEvent?.(Events.CLICKED_PAGINATION_PREVIOUS_PAGE, {
      from: location.pathname,
    })
  }

  return (
    <div className={styles['bookings-table-wrapper']}>
      <table className={styles['bookings-table']} {...getTableProps()}>
        <TableHead headerGroups={headerGroups} />

        <TableBody
          page={page}
          prepareRow={prepareRow}
          tableBodyProps={getTableBodyProps()}
          audience={audience}
          reloadBookings={reloadBookings}
          bookingId={bookingId}
        />
      </table>

      <Pagination
        currentPage={pageIndex + 1}
        pageCount={pageCount}
        onPreviousPageClick={goToPreviousPage}
        onNextPageClick={goToNextPage}
      />
    </div>
  )
}

export default TableWrapper
