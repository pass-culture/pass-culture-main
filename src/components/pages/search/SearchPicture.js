import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../../utils/config'

export const SearchPicture = ({ category }) => (
  <div className="search-picture is-relative">
    <img
      alt={`Rechercher des offres de type ${category}`}
      src={`${ROOT_PATH}/icons/img-${category}.png`}
    />
    <span className="is-absolute text-left fs15">
      {category}
    </span>
  </div>
)

SearchPicture.propTypes = {
  category: PropTypes.string.isRequired,
}
