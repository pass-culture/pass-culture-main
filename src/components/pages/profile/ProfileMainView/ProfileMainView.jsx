import PropTypes from 'prop-types'
import React from 'react'

import { version } from '../../../../../package.json'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import ListLinks from '../ListLinks/ListLinks'
import ProfileHeader from '../ProfileHeader/ProfileHeader'
import RemainingCredit from '../RemainingCredit/RemainingCredit'

const ProfileMainView = ({ currentUser }) => (
  <div className="pm-wrapper">
    <main className="pm-main">
      <div className="pm-scroll">
        <ProfileHeader currentUser={currentUser} />
        <RemainingCredit currentUser={currentUser} />
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
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.shape()]).isRequired,
}

export default ProfileMainView
