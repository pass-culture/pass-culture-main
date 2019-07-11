import PropTypes from 'prop-types'
import React from 'react'

import ProfilePicture from '../../layout/ProfilePicture'

const MonAvatar = ({ currentUser }) => (
  <div
    className="padded flex-columns"
    id="mon-avatar"
  >
    <div className="flex-columns items-center flex-1 my22">
      <ProfilePicture
        className="flex-0"
        colored="colored"
        style={{ height: 80, minHeight: 80, minWidth: 80, width: 80 }}
      />
      <span className="flex-1 ml12 is-medium fs18">
        {currentUser.publicName}
      </span>
    </div>
  </div>
)

MonAvatar.propTypes = {
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.object])
    .isRequired,
}

export default MonAvatar
