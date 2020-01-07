import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'

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
      <main className="mosaic-background pc-main padded is-relative flex-1 flex-rows text-center">
        <h2 className="is-block fs22">
          <Icon
            className="big-success"
            svg="ico-check-w"
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
        extraClassName="dotted-top-red"
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
