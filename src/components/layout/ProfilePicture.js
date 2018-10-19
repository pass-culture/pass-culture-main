import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../utils/config'

const ProfilePicture = ({ colored, ...props }) => {
  const src = `${ROOT_PATH}/icons/ico-user-circled${colored ? '' : '-w'}.svg`
  return <img src={src} alt="Avatar" {...props} />
}

ProfilePicture.defaultProps = {
  colored: false,
}

ProfilePicture.propTypes = {
  colored: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
}

export default ProfilePicture
