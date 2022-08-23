import React from 'react'
import { TableInstance } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import TableBody from './Body/TableBody'
import TableHead from './Head/TableHead'
import TablePagination from './Paginate/TablePagination'

interface TableWrapperProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  canNextPage: TableInstance<T>['canNextPage']
  canPreviousPage: TableInstance<T>['canPreviousPage']
  getTableBodyProps: TableInstance<T>['getTableBodyProps']
  getTableProps: TableInstance<T>['getTableProps']
  headerGroups: TableInstance<T>['headerGroups']
  nbPages: number
  nextPage: TableInstance<T>['nextPage']
  page: TableInstance<T>['page']
  pageIndex: TableInstance<T>['state']['pageIndex']
  prepareRow: TableInstance<T>['prepareRow']
  previousPage: TableInstance<T>['previousPage']
  updateCurrentPage: (pageNumber: number) => void
}

const TableWrapper = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  canNextPage,
  canPreviousPage,
  getTableBodyProps,
  getTableProps,
  headerGroups,
  nbPages,
  nextPage,
  previousPage,
  page,
  pageIndex,
  prepareRow,
  updateCurrentPage,
}: TableWrapperProps<T>): JSX.Element => {
  const goToNextPage = () => {
    nextPage()
    updateCurrentPage(pageIndex + 1)
  }

  const goToPreviousPage = () => {
    previousPage()
    updateCurrentPage(pageIndex - 1)
  }

  return (
    <div className="bookings-table-wrapper">
      <table className="bookings-table" {...getTableProps()}>
        <TableHead headerGroups={headerGroups} />
        <TableBody
          page={page}
          prepareRow={prepareRow}
          tableBodyProps={getTableBodyProps()}
        />
      </table>
      <TablePagination
        canNextPage={canNextPage}
        canPreviousPage={canPreviousPage}
        currentPage={pageIndex + 1}
        nbPages={nbPages}
        nextPage={goToNextPage}
        previousPage={goToPreviousPage}
      />
    </div>
  )
}

export default TableWrapper
