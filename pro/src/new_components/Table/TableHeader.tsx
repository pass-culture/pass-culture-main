import React from 'react'

import Icon from 'components/layout/Icon'

const IS_MULTI_SORT_ACTIVATED = false
// should remove any everywhere bro
const handleOnKeyDown = ({ column, selector }: any) => (event: any) => {
  const enterKeyHasBeenPressed = event.key === 'Enter'
  if (enterKeyHasBeenPressed) {
    column.toggleSortBy(selector, IS_MULTI_SORT_ACTIVATED)
  }
}

const TableHead = ({ headerGroups }: any) => {
  return (
    <thead className="bookings-head">
    {headerGroups.map((headerGroup: any) => (
      <tr key="header-group">

        {headerGroup.headers.map((column: any) => (
          <th
            className={column.className}
            key={column.id}
          >
            {column.canSort ? (
              <span className="sorting-icons">
                  {column.isSorted ? (
                    column.isSortedDesc ? (
                      <Icon
                        onKeyDown={handleOnKeyDown(column)}
                        role="button"
                        svg="ico-arrow-up-r"
                        tabIndex={0} png={undefined} alt={undefined}
                      />
                    ) : (
                      <Icon
                        onKeyDown={handleOnKeyDown(column)}
                        role="button"
                        svg="ico-arrow-down-r"
                        tabIndex={0} png={undefined} alt={undefined}
                      />
                    )
                  ) : (
                    <Icon
                      onKeyDown={handleOnKeyDown(column)}
                      role="button"
                      svg="ico-unfold"
                      tabIndex={0} png={undefined} alt={undefined}
                    />
                  )}
                </span>
            ) : (
              ''
            )}
          </th>
        ))}
      </tr>
    ))}
    </thead>
  )
}

export default TableHead
