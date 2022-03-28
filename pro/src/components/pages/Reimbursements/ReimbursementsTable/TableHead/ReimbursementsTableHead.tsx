import React from 'react'

import Icon from 'components/layout/Icon'

type ColumnOptionType = {
  title: string
  sortBy: string
  selfDirection: string
}

interface IReimbursementsTableHead {
  columns: ColumnOptionType[]
  sortBy: (sortBy: string) => void
}

const ReimbursementsTableHead = ({
  columns,
  sortBy,
}: IReimbursementsTableHead): JSX.Element => {
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
          const ico =
            column.selfDirection === 'default'
              ? { label: 'trier par ordre croissant', type: 'ico-unfold' }
              : column.selfDirection === 'desc'
              ? {
                  label: 'annuler le tri sur cette colonne',
                  type: 'ico-arrow-up-r',
                }
              : {
                  label: 'trier par ordre décroissant',
                  type: 'ico-arrow-down-r',
                }
          return column.selfDirection !== 'None' ? (
            <th key={column.title}>
              <button
                onClick={() => {
                  sortAndChangeColumnDirection(column)
                }}
                title={ico.label}
                type="button"
              >
                {column.title}
                {column.selfDirection !== 'None' && (
                  <Icon alt={ico.label} png="" svg={ico.type} />
                )}
              </button>
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
