import PropTypes from 'prop-types'
import React from 'react'

import { version } from '../../../../../package.json'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import ProfileHeader from '../ProfileHeader/ProfileHeader'
import RemainingCredit from '../RemainingCredit/RemainingCredit'
import User from '../ValueObjects/User'
import ListLinksContainer from '../ListLinks/ListLinksContainer'

const ProfileMainView = ({ user, historyPush }) => (
  <div className="pm-wrapper">
    <main className="pm-main">
      <div className="pm-scroll">
        <ProfileHeader user={user} />
        <RemainingCredit user={user} />
        <ListLinksContainer historyPush={historyPush} />
        <section className="profile-section">
          <div className="pm-app-version">
            {`Version ${version}`}
          </div>
          <img
            alt=""
            className="pm-ministry-of-culture"
            src="/min-culture-rvb@2x.png"
            width="161"
          />
        </section>
      </div>
    </main>
    <RelativeFooterContainer
      extraClassName="dotted-top-red"
      theme="white"
    />
  </div>
)

ProfileMainView.propTypes = {
  historyPush: PropTypes.func.isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default ProfileMainView
