import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const ProfilePicture = ({ colored, ...props }) => {
  const src = `${ROOT_PATH}/icons/ico-user-circled${colored ? '' : '-w'}.svg`
  return <img src={src} alt="Avatar" {...props} />
}

export default ProfilePicture
