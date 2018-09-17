/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Scrollbars } from 'react-custom-scrollbars'

import { ROOT_PATH } from '../../utils/config'
import MonAvatar from './views/MonAvatar'
import PageHeader from '../layout/PageHeader'
// import MonPassCulture from './views/MonPassCulture'
import MesInformations from './views/MesInformations'
import NavigationFooter from '../layout/NavigationFooter'

const ProfileMainView = ({ user, fields }) => {
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
          <MonAvatar user={user} fields={fields} />
          {/* <MonPassCulture user={user} /> */}
          <MesInformations user={user} fields={fields} />
        </Scrollbars>
      </main>
      <NavigationFooter theme="white" />
    </div>
  )
}

ProfileMainView.propTypes = {
  fields: PropTypes.array.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default connect(mapStateToProps)(ProfileMainView)
