import React from 'react'
import PropTypes from 'prop-types'
import Paginate from './Paginate/Paginate'
import Head from './Head/Head'
import Body from './Body/Body'

class Table extends React.Component {
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
          nbPages={nbPages}
          nextPage={this.goToNextPage}
          previousPage={this.goToPreviousPage}
        />
      </div>
    )
  }
}

Table.propTypes = {
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

export default Table
