import PropTypes from 'prop-types'
import React from 'react'

import ProfilePicture from '../../../layout/ProfilePicture/ProfilePicture'

const MonAvatar = ({ currentUser }) => (
  <div className="mon-avatar">
    <ProfilePicture colored="colored" />
    <span>
      {currentUser.publicName}
    </span>
  </div>
)

MonAvatar.propTypes = {
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.shape()]).isRequired,
}

export default MonAvatar
