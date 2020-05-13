import React from 'react'
import PropTypes from 'prop-types'

const Head = ({ headerGroups }) => (
  <thead>
    {headerGroups.map(headerGroup => (
      <tr key={headerGroup.id}>
        {headerGroup.headers.map(column => (
          <th key={column.id}>
            {column.render('headerTitle')}
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
