import React from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../../../layout/Icon'

const Head = ({ headerGroups }) => (
  <thead className="bookings-head">
    {headerGroups.map((headerGroup) => (
      <tr key='header-group'>
        {headerGroup.headers.map(column => (
          <th
            {...column.getHeaderProps(column.getSortByToggleProps())}
            key={column.id}
          >
            {column.render('headerTitle')}
            {column.Filter ? column.render('Filter') : null}
            {
              column.canSort ?
                <span>
                  {column.isSorted ?
                    column.isSortedDesc ? <Icon svg="ico-arrow-up-r" /> : <Icon svg="ico-arrow-down-r" />
                    : <Icon svg="ico-unfold" />}
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
        })
      ),
    })
  ).isRequired,
}

export default Head
