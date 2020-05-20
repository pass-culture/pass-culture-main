import React from 'react'
import PropTypes from 'prop-types'

import { usePagination, useTable } from 'react-table'
import Paginate from './Paginate/Paginate'
import Head from './Head/Head'
import Body from './Body/Body'

const Table = ({
  columns,
  data,
  nbBookings,
  nbBookingsPerPage,
  currentPage,
  updateCurrentPage,
}) => {
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

  function goToNextPage() {
    nextPage()
    updateCurrentPage(currentPage + 1)
  }

  function goToPreviousPage() {
    previousPage()
    updateCurrentPage(currentPage - 1)
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
        nextPage={goToNextPage}
        previousPage={goToPreviousPage}
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
