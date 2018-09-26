/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../../utils/config'
import MonAvatar from './MonAvatar'
import PageHeader from '../../layout/PageHeader'
// import MonPassCulture from './MonPassCulture'
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
        <MonAvatar user={user} />
        {/* <MonPassCulture user={user} /> */}
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
