/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import PageHeader from '../layout/PageHeader'
import NavigationFooter from '../layout/NavigationFooter'

import { ROOT_PATH } from '../../utils/config'

const ProfileUpdateSuccess = ({ user }) => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  const { publicName } = user
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
        <h1>
          <span>
            Bravo
            {publicName} votre profil a été mis à jour
          </span>
        </h1>
      </main>
      <NavigationFooter theme="red" />
    </div>
  )
}

ProfileUpdateSuccess.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default connect(mapStateToProps)(ProfileUpdateSuccess)
