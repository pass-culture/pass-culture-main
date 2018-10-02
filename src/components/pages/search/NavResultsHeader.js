import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../../utils/config'

const NavResultsHeader = ({ searchType, typeSublabels }) => {
  const searchTypeWithoutSpecialChar = searchType.replace(/É/g, 'E')
  const src = `${ROOT_PATH}/icons/img-${searchTypeWithoutSpecialChar}.png`
  const description = `Liste des offres de type ${searchType}`
  return (
    <div id="nav-results-header">
      <div>
        <h2>
          {searchType}
        </h2>
      </div>
      <div>
        {typeSublabels.description}
      </div>

      <img src={src} alt={description} />
    </div>
  )
}

NavResultsHeader.defaultProps = {
  searchType: null,
}

NavResultsHeader.propTypes = {
  searchType: PropTypes.string,
  typeSublabels: PropTypes.object.isRequired,
}

export default NavResultsHeader
