import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../../utils/config'

const NavResultsHeader = ({ category, description }) => {
  const searchTypeWithoutSpecialChar = category.replace(/É/g, 'E')
  const src = `${ROOT_PATH}/icons/img-${searchTypeWithoutSpecialChar}-L.jpg`
  const imgDescription = `Liste des offres de type ${category}`
  return (
    <div
      id="nav-results-header"
      className="p12"
      title={imgDescription}
      style={{
        backgroundImage: `url(${src})`,
      }}
    >
      <div id="category-description" className="text-left is-white-text">
        <h2 className="is-bold mb3">
          {category}
        </h2>
        <span>
          {description}
        </span>
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
