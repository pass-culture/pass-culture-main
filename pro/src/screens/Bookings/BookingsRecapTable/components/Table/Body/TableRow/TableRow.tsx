import React from 'react'
import type { ColumnInstance, Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

interface ITableBodyProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  row: Row<T>
}

const TableRow = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  row,
}: ITableBodyProps<T>) => {
  return (
    <tr {...row.getRowProps()}>
      {row.cells.map(cell => {
        const column: ColumnInstance<T> & { className?: string } = cell.column
        return (
          <td {...cell.getCellProps({ className: column.className })}>
            {cell.render('Cell')}
          </td>
        )
      })}
    </tr>
  )
}

export default TableRow
