import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../../utils/config'

const NavResultsHeader = ({ category, description }) => {
  const src = `${ROOT_PATH}/icons/img-${category}-L.jpg`
  const imgDescription = `Liste des offres de type ${category}`

  return (
    <div
      id="nav-results-header"
      style={{
        backgroundImage: `url(${src})`,
      }}
      title={imgDescription}
    >
      <div id="category-description">
        <h2 className="nav-result-title">{category}</h2>
        <span className="nav-result-description">{description}</span>
      </div>
    </div>
  )
}

NavResultsHeader.defaultProps = {
  category: null,
  description: null,
}

NavResultsHeader.propTypes = {
  category: PropTypes.string,
  description: PropTypes.string,
}

export default NavResultsHeader
