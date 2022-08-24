import React from 'react'
import type { ColumnInstance, TableInstance, TableBodyProps } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

interface ITableBodyProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  page: TableInstance<T>['page']
  prepareRow: TableInstance<T>['prepareRow']
  tableBodyProps: TableBodyProps
}

const TableBody = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  page,
  prepareRow,
  tableBodyProps,
}: ITableBodyProps<T>) => {
  return (
    <tbody className="bookings-body" {...tableBodyProps}>
      {page.map(row => {
        prepareRow(row)
        return (
          <tr {...row.getRowProps()}>
            {row.cells.map(cell => {
              const column: ColumnInstance<T> & { className?: string } =
                cell.column
              return (
                <td {...cell.getCellProps({ className: column.className })}>
                  {cell.render('Cell')}
                </td>
              )
            })}
          </tr>
        )
      })}
    </tbody>
  )
}

export default TableBody
