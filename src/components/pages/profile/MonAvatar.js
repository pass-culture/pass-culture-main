import React from 'react'
import PropTypes from 'prop-types'

import ProfilePicture from '../../layout/ProfilePicture'

const noop = () => {}

const UserAvatar = ({ provider }) => (
  <div id="mon-avatar" className="padded flex-columns">
    <span className="flex-1 my22">
      <ProfilePicture colored="colored" style={{ height: 80, width: 80 }} />
      {provider &&
        provider.thumb && <img alt="Mon Avatar" src={provider.thumb} />}
      <b className="ml12" style={{ fontSize: '1.2rem' }}>
        {provider.publicName}
      </b>
    </span>
    <button
      disabled
      type="button"
      onClick={noop}
      className="no-border no-background flex-0"
    >
      <span
        aria-hidden
        className="icon-next"
        title="Modifier Mes Notifications"
      />
    </button>
  </div>
)

UserAvatar.defaultProps = {}

UserAvatar.propTypes = {
  provider: PropTypes.object.isRequired,
}

export default UserAvatar
