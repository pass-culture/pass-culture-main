import PropTypes from 'prop-types'
import React from 'react'
import { usePagination, useSortBy, useTable } from 'react-table'

import TableWrapper from './TableWrapper'

const TableFrame = ({
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
    useSortBy,
    usePagination
  )
  const pageCount = Math.ceil(nbBookings / nbBookingsPerPage)

  return (
    <TableWrapper
      canNextPage={canNextPage}
      canPreviousPage={canPreviousPage}
      getTableBodyProps={getTableBodyProps}
      getTableProps={getTableProps}
      headerGroups={headerGroups}
      nbPages={pageCount}
      nextPage={nextPage}
      page={page}
      pageIndex={pageIndex}
      prepareRow={prepareRow}
      previousPage={previousPage}
      updateCurrentPage={updateCurrentPage}
    />
  )
}

TableFrame.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      headerTitle: PropTypes.string,
      accessor: PropTypes.string,
      Cell: PropTypes.func,
    })
  ).isRequired,
  currentPage: PropTypes.number.isRequired,
  data: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  nbBookings: PropTypes.number.isRequired,
  nbBookingsPerPage: PropTypes.number.isRequired,
  updateCurrentPage: PropTypes.func.isRequired,
}

export default TableFrame
