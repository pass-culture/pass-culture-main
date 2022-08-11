import React, { useCallback, useEffect, useState } from 'react'

import { InvoiceResponseModel } from 'apiClient/v1'

import styles from './ReimbursementsTable.module.scss'
import ReimbursementsTableBody from './TableBody/ReimbursementsTableBody'
import ReimbursementsTableHead from './TableHead/ReimbursementsTableHead'

type TColumn = {
  title: string
  sortBy: string
  selfDirection: string
}

interface ITableProps {
  columns: TColumn[]
  invoices: InvoiceResponseModel[]
}

const IS_ASCENDENT = 'asc'
const IS_DESCENDENT = 'desc'
const DEFAULT_DIRECTION = IS_ASCENDENT

const ReimbursementsTable = ({
  invoices,
  columns,
}: ITableProps): JSX.Element => {
  const [direction, setDirection] = useState(DEFAULT_DIRECTION)
  const [selectedColumn, setSelectedColumn] = useState('date')
  const [sortedInvoices, setSortedInvoices] = useState([...invoices])

  const changeDirection = (directionToChange: string) =>
    directionToChange === IS_ASCENDENT ? IS_DESCENDENT : IS_ASCENDENT
  const sortBy = useCallback(
    (fieldToSort: string, sortDirection: string) => {
      const newSortedInvoices = invoices.sort((columnA, columnB) => {
        const stringA = columnA[fieldToSort as keyof InvoiceResponseModel] || ''
        const stringB = columnB[fieldToSort as keyof InvoiceResponseModel] || ''
        if (stringA < stringB) return sortDirection === IS_ASCENDENT ? -1 : 1
        if (stringA > stringB) return sortDirection === IS_ASCENDENT ? 1 : -1
        return 0
      })
      setSortedInvoices(newSortedInvoices)
    },
    [invoices]
  )

  const targetedColumn = useCallback(
    (newSelectedColumn: string) => {
      const newDirection =
        newSelectedColumn === selectedColumn
          ? changeDirection(direction)
          : DEFAULT_DIRECTION

      sortBy(newSelectedColumn, newDirection)
      setSelectedColumn(newSelectedColumn)
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
