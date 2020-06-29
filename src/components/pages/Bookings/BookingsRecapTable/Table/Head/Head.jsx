import React from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../../../layout/Icon'

const Head = ({headerGroups}) => (
  <thead className="bookings-head">
    {headerGroups.map(headerGroup => (
      <tr key="header-group">
        {headerGroup.headers.map(column => (
          <th
            {...column.getHeaderProps(column.getSortByToggleProps())}
            className={column.className}
            key={column.id}
          >
            {column.render('headerTitle')}
            {column.Filter ? column.render('Filter') : null}
            {
            column.canSort ?
              <span className="sorting-icons">
                {column.isSorted ?
                    column.isSortedDesc ?
                      <Icon
                        onKeyDown={() => column.toggleSortBy(!column.isSortedDesc)}
                        role="button"
                        svg="ico-arrow-up-r"
                        tabIndex={0}
                      /> :
                      <Icon
                        onKeyDown={() => column.toggleSortBy(!column.isSortedDesc)}
                        role="button"
                        svg="ico-arrow-down-r"
                        tabIndex={0}
                      /> :
                      <Icon
                        onKeyDown={() => column.toggleSortBy(!column.isSortedDesc)}
                        role="button"
                        svg="ico-unfold"
                        tabIndex={0}
                      />}
              </span> :
              ''
          }
          </th>
      ))}
      </tr>
  ))}
  </thead>
)

Head.propTypes = {
  headerGroups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number,
      headers: PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.number,
          headerTitle: PropTypes.string,
          render: PropTypes.func,
        }),
      ),
    }),
  ).isRequired,
}

export default Head
