import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const ProfilePicture = ({ colored }) => {
  const src =
    `${ROOT_PATH}/icons/ico-user-circled` + (colored ? '' : '-w') + `.svg`
  return <img src={src} alt="Avatar" {...this.props} />
}

export default ProfilePicture
