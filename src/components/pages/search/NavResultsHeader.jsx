import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../../utils/config'

const NavResultsHeader = ({ category, description }) => {
  const src = `${ROOT_PATH}/icons/img-${category}-L.jpg`
  const imgDescription = `Liste des offres de type ${category}`

  return (
    <div
      className="p12 is-relative"
      id="nav-results-header"
      style={{
        backgroundImage: `url(${src})`,
      }}
      title={imgDescription}
    >
      <div
        className="text-left is-white-text is-absolute mx12"
        id="category-description"
      >
        <h2 className="is-bold mb3">{category}</h2>
        <span className="fs13 is-medium">{description}</span>
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
