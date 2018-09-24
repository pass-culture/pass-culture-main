import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../../utils/config'

const SearchPicture = ({ searchType, ...props }) => {
  const src = `${ROOT_PATH}/icons/img-${searchType}.png`
  console.log('src >>>>', src)
  return <img src={src} alt="Avatar" {...props} />
}

SearchPicture.defaultProps = {
  searchType: null,
}

SearchPicture.propTypes = {
  searchType: PropTypes.string,
}

export default SearchPicture
