import React from 'react'
import type { Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import TableRow from './TableRow'

interface TableBodyProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
> {
  row: Row<T>
}

// This component goal is to keep consistency with CollectiveTableRow
const IndividualTableRow = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  row,
}: TableBodyProps<T>) => <TableRow row={row} />

export default IndividualTableRow
