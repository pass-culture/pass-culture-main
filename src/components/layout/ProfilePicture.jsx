import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const ProfilePicture = ({ colored }) => {
  const src =
    `${ROOT_PATH}/icons/ico-user-circled` + (colored ? '' : '-w') + `.svg`
  return (<img
    alt="Avatar"
    src={src}
    {...this.props}
          />)
}

export default ProfilePicture
