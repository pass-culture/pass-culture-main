import React from 'react'
import PropTypes from 'prop-types'

import ProfilePicture from '../../layout/ProfilePicture'

const MonAvatar = ({ user }) => (
  <div id="mon-avatar" className="padded flex-columns">
    <div className="flex-columns items-center flex-1 my22">
      <ProfilePicture
        colored="colored"
        className="flex-0"
        style={{ height: 80, minHeight: 80, minWidth: 80, width: 80 }}
      />
      <span className="flex-1 ml12 is-medium fs18">
        {user.publicName}
      </span>
    </div>
  </div>
)

MonAvatar.defaultProps = {}

MonAvatar.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

export default MonAvatar
