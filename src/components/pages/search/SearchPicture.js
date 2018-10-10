import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../../utils/config'

const SearchPicture = ({ searchType }) => {
  const searchTypeWithoutSpecialChar = searchType.replace(/É/g, 'E')
  const src = `${ROOT_PATH}/icons/img-${searchTypeWithoutSpecialChar}.png`
  const navigation = `Rechercher des offres de type ${searchType}`
  return (
    <div className="search-picture is-relative">
      <img src={src} alt={navigation} />
      <span
        style={{ backgroundOpacity: 0.75 }}
        className="is-absolute text-left fs20"
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
