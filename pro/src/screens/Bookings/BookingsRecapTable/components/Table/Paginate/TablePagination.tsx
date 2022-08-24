import React from 'react'
import { TableInstance } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import Icon from 'components/layout/Icon'

interface TablePaginationProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  canNextPage: TableInstance<T>['canNextPage']
  canPreviousPage: TableInstance<T>['canPreviousPage']
  currentPage: number
  nbPages: number
  nextPage: TableInstance<T>['nextPage']
  previousPage: TableInstance<T>['previousPage']
}

const TablePagination = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  canNextPage,
  canPreviousPage,
  currentPage,
  previousPage,
  nbPages,
  nextPage,
}: TablePaginationProps<T>) => (
  <div className="paginate-wrapper">
    <button disabled={!canPreviousPage} onClick={previousPage} type="button">
      <Icon svg="ico-left-arrow" />
    </button>
    <span>{`Page ${currentPage}/${nbPages}`}</span>
    <button disabled={!canNextPage} onClick={nextPage} type="button">
      <Icon svg="ico-right-arrow" />
    </button>
  </div>
)

export default TablePagination
