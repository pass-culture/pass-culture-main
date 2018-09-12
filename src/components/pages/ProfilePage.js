/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withLogin } from 'pass-culture-shared'
import { Scrollbars } from 'react-custom-scrollbars'

import { ROOT_PATH } from '../../utils/config'
import Loader from '../layout/Loader'
import MonAvatar from './profile/MonAvatar'
import PageHeader from '../layout/PageHeader'
// import MonPassCulture from './profile/MonPassCulture'
import MesInformations from './profile/MesInformations'
import NavigationFooter from '../layout/NavigationFooter'

const ProfilePage = ({ user }) => {
  const isloaded = user || typeof user === 'object'
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  return (
    <div id="profile-page" className="page is-relative flex-rows">
      {isloaded && (
        <React.Fragment>
          <PageHeader theme="red" title="Mon profil" />
          <main
            role="main"
            className="is-relative flex-1"
            style={{ backgroundImage }}
          >
            <Scrollbars autoHide>
              <MonAvatar provider={user} />
              {/* {user.expenses && <MonPassCulture provider={user} />} */}
              <MesInformations provider={user} />
            </Scrollbars>
          </main>
          <NavigationFooter theme="red" className="dotted-top-white" />
        </React.Fragment>
      )}
      <Loader isloading={!isloaded} />
    </div>
  )
}

ProfilePage.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(ProfilePage)
