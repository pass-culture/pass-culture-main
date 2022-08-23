import React from 'react'
import { Column, usePagination, useSortBy, useTable } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import TableWrapper from './TableWrapper'

interface TableFrameProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  columns: Column<T>[]
  currentPage: number
  data: T[]
  nbBookings: number
  nbBookingsPerPage: number
  updateCurrentPage: (pageNumber: number) => void
}

const TableFrame = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  columns,
  data,
  nbBookings,
  nbBookingsPerPage,
  currentPage,
  updateCurrentPage,
}: TableFrameProps<T>) => {
  const {
    canPreviousPage,
    canNextPage,
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
    usePagination
  )

  const pageCount = Math.ceil(nbBookings / nbBookingsPerPage)

  return (
    <TableWrapper
      canNextPage={canNextPage}
      canPreviousPage={canPreviousPage}
      getTableBodyProps={getTableBodyProps}
      getTableProps={getTableProps}
      headerGroups={headerGroups}
      nbPages={pageCount}
      nextPage={nextPage}
      page={page}
      pageIndex={pageIndex}
      prepareRow={prepareRow}
      previousPage={previousPage}
      updateCurrentPage={updateCurrentPage}
    />
  )
}

export default TableFrame
