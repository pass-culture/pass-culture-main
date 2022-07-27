/*eslint no-undef: 0*/
import PropTypes from 'prop-types'
import React from 'react'

import TableBody from './Body/TableBody'
import TableHead from './Head/TableHead'
import TablePagination from './Paginate/TablePagination'

class TableWrapper extends React.Component {
  goToNextPage = () => {
    const { pageIndex, nextPage, updateCurrentPage } = this.props
    nextPage()
    updateCurrentPage(pageIndex + 1)
  }

  goToPreviousPage = () => {
    const { pageIndex, previousPage, updateCurrentPage } = this.props
    previousPage()
    updateCurrentPage(pageIndex - 1)
  }

  render() {
    const {
      canNextPage,
      canPreviousPage,
      headerGroups,
      nbPages,
      page,
      pageIndex,
      prepareRow,
      getTableProps,
      getTableBodyProps,
    } = this.props
    return (
      <div className="bookings-table-wrapper">
        <table className="bookings-table" {...getTableProps()}>
          <TableHead headerGroups={headerGroups} />
          <TableBody
            page={page}
            prepareRow={prepareRow}
            tableBodyProps={getTableBodyProps()}
          />
        </table>
        <TablePagination
          canNextPage={canNextPage}
          canPreviousPage={canPreviousPage}
          currentPage={pageIndex + 1}
          nbPages={nbPages}
          nextPage={this.goToNextPage}
          previousPage={this.goToPreviousPage}
        />
      </div>
    )
  }
}

TableWrapper.propTypes = {
  canNextPage: PropTypes.bool.isRequired,
  canPreviousPage: PropTypes.bool.isRequired,
  getTableBodyProps: PropTypes.func.isRequired,
  getTableProps: PropTypes.func.isRequired,
  headerGroups: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  nbPages: PropTypes.number.isRequired,
  nextPage: PropTypes.func.isRequired,
  page: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  pageIndex: PropTypes.number.isRequired,
  prepareRow: PropTypes.func.isRequired,
  previousPage: PropTypes.func.isRequired,
  updateCurrentPage: PropTypes.func.isRequired,
}

export default TableWrapper
