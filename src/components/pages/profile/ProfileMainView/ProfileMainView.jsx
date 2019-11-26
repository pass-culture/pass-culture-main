import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../../../utils/config'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import MesInformations from '../MesInformations/MesInformations'
import MonAvatar from '../MonAvatar/MonAvatar'
import MonPassCulture from '../MonPassCulture/MonPassCulture'

const BACKGROUND_IMAGE = `url('${ROOT_PATH}/mosaic-k.png')`

const ProfileMainView = ({ config, currentUser }) => (
  <div
    className="pc-page-view pc-theme-default flex-rows with-header"
    id="profile-page-main-view"
  >
    <HeaderContainer title="Mon compte" />
    <main
      className="pc-main is-clipped is-relative"
      style={{ backgroundImage: BACKGROUND_IMAGE }}
    >
      <div className="pc-scroll-container">
        {currentUser && <MonAvatar currentUser={currentUser} />}
        <div id="profile-page-user-passculture">
          <h3 className="dotted-bottom-primary pb8 px12 is-italic is-uppercase is-primary-text fs15 is-normal">
            {'Mon pass Culture'}
          </h3>
          <div className="mt12 px12">
            {currentUser && <MonPassCulture currentUser={currentUser} />}
          </div>
        </div>
        <MesInformations
          fields={config}
          user={currentUser}
        />
      </div>
    </main>
    <RelativeFooterContainer
      className="dotted-top-red"
      theme="white"
    />
  </div>
)

ProfileMainView.propTypes = {
  config: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.shape()]).isRequired,
}

export default ProfileMainView
