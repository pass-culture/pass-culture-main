import React from 'react'
import type { TableInstance, TableBodyProps, Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'

import CollectiveTableRow from './TableRow/CollectiveTableRow'
import IndividualTableRow from './TableRow/IndividualTableRow'

interface ITableBodyProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  page: TableInstance<T>['page']
  prepareRow: TableInstance<T>['prepareRow']
  tableBodyProps: TableBodyProps
  audience: Audience
}

const isCollectiveRow = (
  row: any,
  audience: Audience
): row is Row<CollectiveBookingResponseModel> =>
  audience === Audience.COLLECTIVE

const TableBody = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  page,
  prepareRow,
  tableBodyProps,
  audience,
}: ITableBodyProps<T>) => {
  return (
    <tbody className="bookings-body" {...tableBodyProps}>
      {page.map(row => {
        prepareRow(row)
        return isCollectiveRow(row, audience) ? (
          <CollectiveTableRow row={row} />
        ) : (
          <IndividualTableRow row={row} />
        )
      })}
    </tbody>
  )
}

export default TableBody
