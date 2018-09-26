import React from 'react'
import PropTypes from 'prop-types'

import ProfilePicture from '../../layout/ProfilePicture'

const MonAvatar = ({ user }) => (
  <div id="mon-avatar" className="padded flex-columns">
    <span className="flex-1 my22">
      <ProfilePicture colored="colored" style={{ height: 80, width: 80 }} />
      {user && user.thumb && <img alt="Mon Avatar" src={user.thumb} />}
      <span className="ml12 is-medium fs18">
        {user.publicName}
      </span>
    </span>
    {/* <button
      disabled
      type="button"
      onClick={() => {}}
      className="no-border no-background flex-0"
    >
      <span
        aria-hidden
        className="icon-next"
        title="Modifier Mes Notifications"
      />
    </button> */}
  </div>
)

MonAvatar.defaultProps = {}

MonAvatar.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

export default MonAvatar
