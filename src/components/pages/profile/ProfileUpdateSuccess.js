import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import { ROOT_PATH } from '../../../utils/config'
import PageHeader from '../../layout/Header/PageHeader'
import NavigationFooter from '../../layout/NavigationFooter'

const BACKGROUND_IMAGE = `url('${ROOT_PATH}/mosaic-k.png')`

const ProfileUpdateSuccess = ({ config, match }) => {
  const item = config[match.params.view]
  return (
    <div
      id="profile-page-main-view"
      className="pc-page-view pc-theme-default flex-rows with-header"
    >
      <PageHeader backTo="/profil" closeTo={null} title={item.title} />
      <main
        role="main"
        style={{ backgroundImage: BACKGROUND_IMAGE }}
        className="pc-main padded is-relative flex-1 flex-rows text-center"
      >
        <h2 className="is-block fs22">
          <span
            aria-hidden
            className="icon-legacy-check-circled big-success-icon"
            title=""
          />
          <span className="is-block mt24">
            {`${item.title} a bien été modifié`}
          </span>
        </h2>
        <div className="mt12">
          Pensez à l&apos;utiliser lors de votre prochaine connexion
        </div>
        <div className="mt24 is-bold fs16">
          <Link to="/profil" className="is-red-text">
            <span>Retour au profil</span>
          </Link>
        </div>
      </main>
      <NavigationFooter theme="white" className="dotted-top-red" />
    </div>
  )
}

ProfileUpdateSuccess.propTypes = {
  config: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
}

export default ProfileUpdateSuccess
