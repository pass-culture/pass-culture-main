import PropTypes from 'prop-types'
import React from 'react'

import { version } from '../../../../../package.json'
import ProfileHeader from '../ProfileHeader/ProfileHeader'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import MesInformationsContainer from '../MesInformations/MesInformationsContainer'
import RemainingCredit from '../RemainingCredit/RemainingCredit'

const ProfileMainView = ({ currentUser }) => (
  <div className="pm-wrapper">
    <main className="pm-main">
      <div className="pm-scroll">
        <ProfileHeader currentUser={currentUser} />
        {currentUser && <RemainingCredit currentUser={currentUser} />}
        <MesInformationsContainer />
        <div className="pm-app-version">
          {`Version ${version}`}
        </div>
        <img
          alt=""
          className="pm-ministry-of-culture"
          src="/min-culture-rvb@2x.png"
          width="161"
        />
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
