import React from 'react'

import Icon from 'components/layout/Icon'

type columnOptionType = {
  title: string
  sortBy: string
  selfDirection: string
}

interface IReimbursementsTableHead {
  columns: [columnOptionType]
  sortBy: (sortBy: string) => void
}

const ReimbursementsTableHead = ({
  columns,
  sortBy,
}: IReimbursementsTableHead): JSX.Element => {
  const changeDirection = (columnOption: columnOptionType) => {
    const otherColumnOption = columns.filter(title => title !== columnOption)

    otherColumnOption.forEach(columnOption => {
      columnOption.selfDirection = 'default'
    })

    if (columnOption.selfDirection === 'default') {
      columnOption.selfDirection = 'asc'
    } else if (columnOption.selfDirection === 'asc') {
      columnOption.selfDirection = 'desc'
    } else {
      columnOption.selfDirection = 'default'
    }
  }

  return (
    <thead>
      <tr>
        {columns.map(column => (
          <th
            key={column.title}
            onClick={() => {
              sortBy(column.sortBy)
              changeDirection(column)
            }}
          >
            {column.title}
            {column.selfDirection === 'default' && (
              <Icon alt="" png="" role="button" svg="ico-unfold" tabIndex={0} />
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
          </th>
        ))}
      </tr>
    </thead>
  )
}

export default ReimbursementsTableHead
