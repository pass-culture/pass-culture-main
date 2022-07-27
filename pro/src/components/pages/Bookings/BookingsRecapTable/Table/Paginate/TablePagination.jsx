import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const TablePagination = ({
  canNextPage,
  canPreviousPage,
  currentPage,
  previousPage,
  nbPages,
  nextPage,
}) => (
  <div className="paginate-wrapper">
    <button disabled={!canPreviousPage} onClick={previousPage} type="button">
      <Icon svg="ico-left-arrow" />
    </button>
    <span>{`Page ${currentPage}/${nbPages}`}</span>
    <button disabled={!canNextPage} onClick={nextPage} type="button">
      <Icon svg="ico-right-arrow" />
    </button>
  </div>
)

TablePagination.propTypes = {
  canNextPage: PropTypes.bool.isRequired,
  canPreviousPage: PropTypes.bool.isRequired,
  currentPage: PropTypes.number.isRequired,
  nbPages: PropTypes.number.isRequired,
  nextPage: PropTypes.func.isRequired,
  previousPage: PropTypes.func.isRequired,
}

export default TablePagination
