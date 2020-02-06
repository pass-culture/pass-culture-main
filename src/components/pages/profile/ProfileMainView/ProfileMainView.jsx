import React from 'react'
import PropTypes from 'prop-types'

import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import MesInformations from '../MesInformations/MesInformations'
import RemainingCredit from '../RemainingCredit/RemainingCredit'

const ProfileMainView = ({ informationsFields, currentUser }) => (
  <div
    className="pc-page-view pc-theme-default flex-rows with-header"
    id="profile-page-main-view"
  >
    <HeaderContainer title="Mon compte" />
    <main className="mosaic-background pc-main is-clipped is-relative">
      <div className="pc-scroll-container">
        {currentUser && <RemainingCredit currentUser={currentUser} />}
        <MesInformations
          fields={informationsFields}
          user={currentUser}
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
  informationsFields: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default ProfileMainView
