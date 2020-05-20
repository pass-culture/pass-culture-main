import React from 'react'
import PropTypes from 'prop-types'

import { usePagination, useTable } from 'react-table'
import Paginate from './Paginate/Paginate'
import Head from './Head/Head'
import Body from './Body/Body'

const Table = ({ columns, data, nbBookings, nbBookingsPerPage, currentPage, foobar }) => {
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
    pageOptions,
    state: { pageIndex },
  } = useTable(
    {
      columns,
      data,
      initialState: {
        pageIndex: currentPage,
        pageSize: nbBookingsPerPage,
      },
    },
    usePagination
  )
  const pageCount = Math.ceil(nbBookings / nbBookingsPerPage)

  const a = () => {
    nextPage()
    foobar(1)
  }

  return (
    <div className="bookings-table-wrapper">
      <table
        className="bookings-table"
        {...getTableProps()}
      >
        <Head headerGroups={headerGroups} />
        <Body
          page={page}
          prepareRow={prepareRow}
          tableBodyProps={getTableBodyProps()}
        />
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
  nbBookings: PropTypes.number.isRequired,
  nbBookingsPerPage: PropTypes.number.isRequired,
}

export default Table
