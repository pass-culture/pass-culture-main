import PropTypes from 'prop-types'
import React from 'react'

const TableBody = ({ page, prepareRow, tableBodyProps }) => {
  return (
    <tbody className="bookings-body" {...tableBodyProps}>
      {page.map(row => {
        prepareRow(row)
        return (
          <tr key={row.id} {...row.getRowProps()}>
            {row.cells.map(cell => {
              return (
                <td
                  key={cell.id}
                  {...cell.getCellProps({ className: cell.column.className })}
                >
                  {cell.render('Cell')}
                </td>
              )
            })}
          </tr>
        )
      })}
    </tbody>
  )
}

TableBody.propTypes = {
  page: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  prepareRow: PropTypes.func.isRequired,
  tableBodyProps: PropTypes.shape().isRequired,
}

export default TableBody
