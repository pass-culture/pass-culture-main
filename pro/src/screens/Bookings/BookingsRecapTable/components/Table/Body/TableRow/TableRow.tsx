import React from 'react'
import type { ColumnInstance, Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import styles from './TableRow.module.scss'
interface TableBodyProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
> {
  row: Row<T>
  isCollective?: boolean
  additionalRowAttribute?: any
}

const TableRow = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  row,
  additionalRowAttribute,
}: TableBodyProps<T>) => {
  const rowAttributes = {
    ...row.getRowProps(),
    ...additionalRowAttribute,
  }
  return (
    <>
      <tr {...rowAttributes} className={styles['table-row']}>
        {row.cells.map(cell => {
          const column: ColumnInstance<T> & { className?: string } = cell.column
          return (
            <td {...cell.getCellProps({ className: column.className })}>
              {cell.render('Cell')}
            </td>
          )
        })}
      </tr>
    </>
  )
}

export default TableRow
