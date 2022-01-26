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
        {columns.map(column => (
          <th
            key={column.title}
            onClick={() => {
              sortAndChangeColumnDirection(column)
            }}
          >
            {column.title}
            {column.selfDirection !== 'None' && (
              <>
                {column.selfDirection === 'default' && (
                  <Icon
                    alt=""
                    png=""
                    role="button"
                    svg="ico-unfold"
                    tabIndex={0}
                  />
                )}
                {column.selfDirection === 'desc' && (
                  <Icon
                    alt=""
                    png=""
                    role="button"
                    svg="ico-arrow-up-r"
                    tabIndex={0}
                  />
                )}
                {column.selfDirection === 'asc' && (
                  <Icon
                    alt=""
                    png=""
                    role="button"
                    svg="ico-arrow-down-r"
                    tabIndex={0}
                  />
                )}
              </>
            )}
          </th>
        ))}
      </tr>
    </thead>
  )
}

export default ReimbursementsTableHead
