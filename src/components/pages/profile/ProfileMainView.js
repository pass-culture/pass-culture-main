/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { ROOT_PATH } from '../../../utils/config'
import MonAvatar from './MonAvatar'
import PageHeader from '../../layout/PageHeader'
// import MonPassCulture from './MonPassCulture'
import MesInformations from './MesInformations'
import NavigationFooter from '../../layout/NavigationFooter'

const ProfileMainView = ({ user, fields }) => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  return (
    <div
      id="profile-page-main-view"
      className="pc-page-view pc-theme-default flex-rows"
    >
      <PageHeader useClose theme="red" title="Mon profil" />
      <main
        role="main"
        className="pc-main is-clipped is-relative"
        style={{ backgroundImage }}
      >
        <div className="pc-scroll-container">
          <MonAvatar user={user} fields={fields} />
          {/* <MonPassCulture user={user} /> */}
          <MesInformations user={user} fields={fields} />
        </div>
      </main>
      <NavigationFooter theme="white" className="dotted-top-red" />
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
