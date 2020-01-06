import PropTypes from 'prop-types'
import React from 'react'

const NavResultsHeader = ({ category, description }) => (
  <div className={`nav-results-header nav-results-${category}`}>
    <div className="nav-results-wrapper">
      <h2 className="nav-results-title">
        {category}
      </h2>
      <div className="nav-results-description">
        {description}
      </div>
    </div>
  </div>
)

NavResultsHeader.propTypes = {
  category: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
}

export default NavResultsHeader
