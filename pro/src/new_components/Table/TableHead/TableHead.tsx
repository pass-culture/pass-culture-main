import React from 'react'

import Icon from 'components/layout/Icon'

interface ITableHead {
  rowTitlesOptions: [
    {
      title: string,
      sortBy: string,
      selfDirection: string
    }
  ],
  sortBy: (sortBy:string)=>void,
}

const TableHead = ({ rowTitlesOptions, sortBy }: ITableHead):JSX.Element => {

  const changeDirection = (titleOption:any) => {
    titleOption.selfDirection === "default" ? titleOption.selfDirection = "asc" :
      titleOption.selfDirection === "asc" ? titleOption.selfDirection = "desc" :
        titleOption.selfDirection === "desc" ? titleOption.selfDirection = "default" : titleOption.selfDirection = "asc"
  }

  return (
    <thead >
      <tr>
        {rowTitlesOptions.map((titleOption) => (
          <th onClick={() => {
            sortBy(titleOption.sortBy)
            changeDirection(titleOption)
          }}
          >
            {titleOption.title}
            {
              titleOption.selfDirection === 'default' && (
                <Icon
                  alt=""
                  png=""
                  role="button"
                  svg="ico-unfold"
                  tabIndex={0}
                />
              )
            }
            {
              titleOption.selfDirection === 'desc' && (
                <Icon
                  alt=""
                  png=""
                  role="button"
                  svg="ico-arrow-up-r"
                  tabIndex={0}
                />
              )
            }
            {
              titleOption.selfDirection === 'asc' && (
                <Icon
                  alt=""
                  png=""
                  role="button"
                  svg="ico-arrow-down-r"
                  tabIndex={0}
                />
              )
            }
          </th>
        ))}
      </tr>
    </thead>
  )
}

export default TableHead
