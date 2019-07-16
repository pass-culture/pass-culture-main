import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const ProfilePicture = ({ colored, ...props }) => (
  <img
    alt="Avatar"
    src={`${ROOT_PATH}/icons/ico-user-circled` + (colored ? '' : '-w') + `.svg`}
    {...props}
  />
)

ProfilePicture.defaultProps = {
  colored: null,
}

ProfilePicture.propTypes = {
  colored: PropTypes.string,
}

export default ProfilePicture
