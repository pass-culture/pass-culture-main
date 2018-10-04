import React from 'react'
import PropTypes from 'prop-types'

// import get from 'lodash.get'

import { ROOT_PATH } from '../../../utils/config'

const NavResultsHeader = ({ category, description }) => {
  const searchTypeWithoutSpecialChar = category.replace(/É/g, 'E')
  const src = `${ROOT_PATH}/icons/img-${searchTypeWithoutSpecialChar}.png`
  const imgDescription = `Liste des offres de type ${category}`
  return (
    <div id="nav-results-header">
      <div className="flex-rows text-right is-white-text">
        <div className="flex-1 fs22 is-bold">
          <h2>
            {category}
          </h2>
        </div>
        <div className="flex-1">
          {description}
        </div>
      </div>
      <img src={src} alt={imgDescription} />
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
