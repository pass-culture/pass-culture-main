import React from 'react'

import { SortArrow } from 'components/StocksEventList/SortArrow'
import { SortingMode } from 'hooks/useColumnSorting'

type ColumnOptionType = {
  title: string
  sortBy: string
  selfDirection: string
}

interface ReimbursementsTableHead {
  columns: ColumnOptionType[]
  sortBy: (sortBy: string) => void
}

const ReimbursementsTableHead = ({
  columns,
  sortBy,
}: ReimbursementsTableHead): JSX.Element => {
  const changeDirection = (columnOption: ColumnOptionType) => {
    if (columnOption.selfDirection === 'None') {
      return
    }

    const otherColumnOption = columns.filter(title => title !== columnOption)

    otherColumnOption.forEach(columnOption => {
      if (columnOption.selfDirection !== 'None') {
        columnOption.selfDirection = 'default'
      }
    })

    if (columnOption.selfDirection === 'default') {
      columnOption.selfDirection = 'asc'
    } else if (columnOption.selfDirection === 'asc') {
      columnOption.selfDirection = 'desc'
    } else {
      columnOption.selfDirection = 'default'
    }
  }

  const sortAndChangeColumnDirection = (columnOption: ColumnOptionType) => {
    if (columnOption.selfDirection === 'None') {
      return
    } else {
      sortBy(columnOption.sortBy)
      changeDirection(columnOption)
    }
  }
  return (
    <thead>
      <tr>
        {columns.map(column => {
          const sortingMode =
            column.selfDirection === 'default'
              ? SortingMode.NONE
              : column.selfDirection === 'desc'
              ? SortingMode.DESC
              : SortingMode.ASC

          return column.selfDirection !== 'None' ? (
            <th key={column.title}>
              {column.title}&nbsp;
              {column.selfDirection !== 'None' && (
                <SortArrow
                  sortingMode={sortingMode}
                  onClick={() => {
                    sortAndChangeColumnDirection(column)
                  }}
                />
              )}
            </th>
          ) : (
            <th key={column.title}>{column.title}</th>
          )
        })}
      </tr>
    </thead>
  )
}

export default ReimbursementsTableHead
