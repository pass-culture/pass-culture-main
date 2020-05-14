import PropTypes from 'prop-types'
import React from 'react'

import { version } from '../../../../../package.json'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import ListLinks from '../ListLinks/ListLinks'
import ProfileHeader from '../ProfileHeader/ProfileHeader'
import RemainingCredit from '../RemainingCredit/RemainingCredit'
import User from '../ValueObjects/User'

const ProfileMainView = ({ user }) => (
  <div className="pm-wrapper">
    <main className="pm-main">
      <div className="pm-scroll">
        <ProfileHeader user={user} />
        <RemainingCredit user={user} />
        <ListLinks />
        <section className="pm-section">
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
  user: PropTypes.instanceOf(User).isRequired,
}

export default ProfileMainView
