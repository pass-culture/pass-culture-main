import React from 'react'
import PropTypes from 'prop-types'

import { usePagination, useTable } from 'react-table'
import Paginate from './Paginate/Paginate'
import Head from './Head/Head'

const FIRST_PAGE_INDEX = 0

const Table = ({ columns, data, nbHitsPerPage }) => {
  const {
    canPreviousPage,
    canNextPage,
    getTableProps,
    getTableBodyProps,
    headerGroups,
    nextPage,
    previousPage,
    prepareRow,
    page,
    pageCount,
    state: { pageIndex },
  } = useTable(
    {
      columns,
      data,
      initialState: {
        pageIndex: FIRST_PAGE_INDEX,
        pageSize: nbHitsPerPage,
      },
    },
    usePagination
  )

  return (
    <div>
      <table
        className="bookings-table"
        {...getTableProps()}
      >
        <Head headerGroups={headerGroups} />

        <tbody {...getTableBodyProps()}>
          {page.map(row => {
            prepareRow(row)
            return (
              <tr
                key={row.id}
                {...row.getRowProps()}
              >
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
      </table>
      <Paginate
        canNextPage={canNextPage}
        canPreviousPage={canPreviousPage}
        currentPage={pageIndex + 1}
        nbPages={pageCount}
        nextPage={nextPage}
        previousPage={previousPage}
      />
    </div>
  )
}

Table.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      headerTitle: PropTypes.string,
      accessor: PropTypes.string,
      Cell: PropTypes.func,
    })
  ).isRequired,
  data: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
}

export default Table
