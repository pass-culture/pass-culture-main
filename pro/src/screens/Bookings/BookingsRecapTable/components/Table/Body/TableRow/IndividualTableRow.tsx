import React from 'react'
import type { Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import TableRow from './TableRow'

interface ITableBodyProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  row: Row<T>
}

// This component goal is to keep consistancy with CollectiveTableRow
const IndividualTableRow = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  row,
}: ITableBodyProps<T>) => <TableRow row={row} />

export default IndividualTableRow
