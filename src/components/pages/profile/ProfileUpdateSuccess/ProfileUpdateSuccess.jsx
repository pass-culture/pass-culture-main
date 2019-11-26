import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import { ROOT_PATH } from '../../../../utils/config'
import Header from '../../../layout/Header/Header'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'

const BACKGROUND_IMAGE = `url('${ROOT_PATH}/mosaic-k.png')`

const ProfileUpdateSuccess = ({ config, match }) => {
  const item = config[match.params.view]
  return (
    <div
      className="pc-page-view pc-theme-default flex-rows with-header"
      id="profile-page-main-view"
    >
      <Header
        backTo="/profil"
        closeTo={null}
        title={item.title}
      />
      <main
        className="pc-main padded is-relative flex-1 flex-rows text-center"
        style={{ backgroundImage: BACKGROUND_IMAGE }}
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
          {'Pensez à l’utiliser lors de votre prochaine connexion'}
        </div>
        <div className="mt24 is-bold fs16">
          <Link
            className="is-red-text"
            to="/profil"
          >
            <span>
              {'Retourner sur mon compte'}
            </span>
          </Link>
        </div>
      </main>
      <RelativeFooterContainer
        className="dotted-top-red"
        theme="white"
      />
    </div>
  )
}

ProfileUpdateSuccess.propTypes = {
  config: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
}

export default ProfileUpdateSuccess
