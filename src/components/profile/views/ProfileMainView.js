/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Scrollbars } from 'react-custom-scrollbars'

import { ROOT_PATH } from '../../../utils/config'
import MonAvatar from '../MonAvatar'
import MesInformations from '../MesInformations'
import PageHeader from '../../layout/PageHeader'
import NavigationFooter from '../../layout/NavigationFooter'

const ProfileMainView = ({ user }) => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  return (
    <div
      id="profile-page-main-view"
      className="pc-page-view-main transition-item pc-theme-default flex-rows"
    >
      <PageHeader theme="red" title="Mon profil" />
      <main
        role="main"
        className="pc-main is-relative flex-1"
        style={{ backgroundImage }}
      >
        <Scrollbars autoHide>
          <MonAvatar provider={user} />
          <MesInformations provider={user} />
        </Scrollbars>
      </main>
      <NavigationFooter theme="red" />
    </div>
  )
}

ProfileMainView.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default connect(mapStateToProps)(ProfileMainView)
