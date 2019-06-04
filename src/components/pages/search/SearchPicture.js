import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../../utils/config'

const SearchPicture = ({ searchType }) => {
  const src = `${ROOT_PATH}/icons/img-${searchType}.png`
  const navigation = `Rechercher des offres de type ${searchType}`

  return (
    <div className="search-picture is-relative">
      <img src={src} alt={navigation} />
      <span
        style={{ backgroundOpacity: 0.75 }}
        className="is-absolute text-left fs15"
      >
        {searchType}
      </span>
    </div>
  )
}

SearchPicture.defaultProps = {
  searchType: null,
}

SearchPicture.propTypes = {
  searchType: PropTypes.string,
}

export default SearchPicture
