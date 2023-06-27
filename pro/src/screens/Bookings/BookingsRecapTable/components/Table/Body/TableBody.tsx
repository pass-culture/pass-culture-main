import React from 'react'
import type {
  TableInstance,
  TableBodyProps as ReactTableTableBodyProps,
  Row,
} from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'

import styles from './TableBody.module.scss'
import CollectiveTableRow from './TableRow/CollectiveTableRow'
import IndividualTableRow from './TableRow/IndividualTableRow'

interface TableBodyProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  page: TableInstance<T>['page']
  prepareRow: TableInstance<T>['prepareRow']
  tableBodyProps: ReactTableTableBodyProps
  audience: Audience
  reloadBookings: () => void
  bookingId: string
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
  reloadBookings,
  bookingId,
}: TableBodyProps<T>) => {
  return (
    <tbody className={styles['bookings-body']} {...tableBodyProps}>
      {page.map((row, index) => {
        prepareRow(row)
        return isCollectiveRow(row, audience) ? (
          <CollectiveTableRow
            key={index}
            row={row}
            reloadBookings={reloadBookings}
            bookingId={bookingId}
          />
        ) : (
          <IndividualTableRow key={index} row={row} />
        )
      })}
    </tbody>
  )
}

export default TableBody
