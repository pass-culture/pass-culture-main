import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../utils/config'

const ProfilePicture = ({ colored, ...props }) => {
  const src = `${ROOT_PATH}/icons/ico-user-circled${colored ? '' : '-w'}.svg`
  return <img src={src} alt="Avatar" {...props} />
}

ProfilePicture.defaultProps = {
  colored: null,
}

ProfilePicture.propTypes = {
  colored: PropTypes.string,
}

export default ProfilePicture
