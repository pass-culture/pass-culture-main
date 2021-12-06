import React from 'react'

import styles from './TableBody.module.scss'

type ColumnData= {
  date: string,
  lieux: string,
  reference: string,
  montant: string,
}

interface ITableBody {
  rows: Array<ColumnData>,
}

const TableBody = ({ rows }: ITableBody): JSX.Element => {

  return (
    <tbody >
      {rows.map((column) => {
        return (
          <tr className={styles[""]}>
            <td className={styles["date"]}>
              {column.date}
            </td>
            <td className={styles["lieux"]}>
              {column.lieux}
            </td>
            <td>
              {column.reference}
            </td>
            <td className={styles["price"]}>
              {column.montant}
            </td>
            <td />
          </tr>
        )
      })}
    </tbody>
  )
}

export default TableBody
