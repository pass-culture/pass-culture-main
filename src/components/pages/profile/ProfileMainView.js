/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../../utils/config'
import MonAvatar from './MonAvatar'
import PageHeader from '../../layout/PageHeader'
import MonPassCulture from './MonPassCulture'
import MesInformations from './MesInformations'
import NavigationFooter from '../../layout/NavigationFooter'

const BACKGROUND_IMAGE = `url('${ROOT_PATH}/mosaic-k.png')`

const ProfileMainView = ({ config, user }) => (
  <div
    id="profile-page-main-view"
    className="pc-page-view pc-theme-default flex-rows"
  >
    <PageHeader useClose theme="red" title="Mon profil" />
    <main
      role="main"
      className="pc-main is-clipped is-relative"
      style={{ backgroundImage: BACKGROUND_IMAGE }}
    >
      <div className="pc-scroll-container">
        {user && <MonAvatar user={user} />}
        {/* <!-- Wallet + Activation --> */}
        <div id="profile-page-user-passculture">
          <h3 className="dotted-bottom-primary pb8 px12">
            <span className="is-italic is-uppercase is-primary-text">
              MON PASS CULTURE
            </span>
          </h3>
          <div className="mt12 px12">
            {user && <MonPassCulture user={user} />}
          </div>
        </div>
        <MesInformations user={user} fields={config} />
      </div>
    </main>
    <NavigationFooter theme="white" className="dotted-top-red" />
  </div>
)

ProfileMainView.propTypes = {
  config: PropTypes.array.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

export default ProfileMainView
