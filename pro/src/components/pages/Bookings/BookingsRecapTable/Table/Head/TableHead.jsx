import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const IS_MULTI_SORT_ACTIVATED = false

const handleOnKeyDown = (column, selector) => event => {
  const enterKeyHasBeenPressed = event.key === 'Enter'
  if (enterKeyHasBeenPressed) {
    column.toggleSortBy(selector, IS_MULTI_SORT_ACTIVATED)
  }
}

const TableHead = ({ headerGroups }) => {
  return (
    <thead className="bookings-head">
      {headerGroups.map(headerGroup => (
        <tr key="header-group">
          {headerGroup.headers.map(column => (
            <th
              {...column.getHeaderProps(column.getSortByToggleProps())}
              className={column.className}
              key={column.id}
            >
              {column.HeaderTitleFilter
                ? column.render('HeaderTitleFilter')
                : column.render('headerTitle')}
              {column.canSort ? (
                <span className="sorting-icons">
                  {column.isSorted ? (
                    column.isSortedDesc ? (
                      <Icon
                        onKeyDown={handleOnKeyDown(column, null)}
                        role="button"
                        svg="ico-arrow-up-r"
                        tabIndex={0}
                      />
                    ) : (
                      <Icon
                        onKeyDown={handleOnKeyDown(column, true)}
                        role="button"
                        svg="ico-arrow-down-r"
                        tabIndex={0}
                      />
                    )
                  ) : (
                    <Icon
                      onKeyDown={handleOnKeyDown(column, false)}
                      role="button"
                      svg="ico-unfold"
                      tabIndex={0}
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

TableHead.propTypes = {
  headerGroups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number,
      headers: PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.number,
          headerTitle: PropTypes.string,
          render: PropTypes.func,
        })
      ),
    })
  ).isRequired,
}

export default TableHead
