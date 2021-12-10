import React, { useCallback, useEffect, useState } from 'react'

import styles from './ReimbursementsTable.module.scss'
import ReimbursementsTableBody from './TableBody/ReimbursementsTableBody'
import ReimbursementsTableHead from './TableHead/ReimbursementsTableHead'

type invoice = {
  date: string
  businessUnitName: string
  reference: string
  amount: string
}

// TODO specify type 'invoice' to invoices Array makes the app crash on line 43, find a solution
interface ITableProps {
  columns: [
    {
      title: string
      sortBy: string
      selfDirection: string
    }
  ]
  invoices: Array<any>
}

const IS_ASCENDENT = 'asc'
const IS_DESCENDENT = 'desc'
const DEFAULT_DIRECTION = IS_ASCENDENT

const ReimbursementsTable = ({
  invoices,
  columns,
}: ITableProps): JSX.Element => {
  const [direction, setDirection] = useState(DEFAULT_DIRECTION)
  const [selectedColumn, setSelectedTitle] = useState('date')
  const [sortedInvoices, setSortedInvoices] = useState([...invoices])

  const changeDirection = (directionToChange: string) =>
    directionToChange === IS_ASCENDENT ? IS_DESCENDENT : IS_ASCENDENT
  const sortBy = useCallback(
    (fieldToSort: string, sortDirection: string) => {
      const newSortedInvoices = invoices.sort((columnA, columnB) => {
        if (columnA[fieldToSort] < columnB[fieldToSort])
          return sortDirection === IS_ASCENDENT ? -1 : 1
        if (columnA[fieldToSort] > columnB[fieldToSort])
          return sortDirection === IS_ASCENDENT ? 1 : -1
        return 0
      })
      setSortedInvoices(newSortedInvoices)
    },
    [invoices]
  )

  const targetedColumn = useCallback(
    newSelectedColumn => {
      const newDirection =
        newSelectedColumn === selectedColumn
          ? changeDirection(direction)
          : DEFAULT_DIRECTION

      sortBy(newSelectedColumn, newDirection)
      setSelectedTitle(newSelectedColumn)
      setDirection(newDirection)
    },
    [selectedColumn, direction, sortBy]
  )

  useEffect(() => {
    sortBy(selectedColumn, direction)
  }, [direction, selectedColumn, sortBy])

  return (
    <table className={styles['reimbursement-table']}>
      <ReimbursementsTableHead columns={columns} sortBy={targetedColumn} />
      <ReimbursementsTableBody invoices={sortedInvoices} />
    </table>
  )
}

export default ReimbursementsTable
