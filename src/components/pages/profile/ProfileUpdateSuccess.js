/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Link, withRouter } from 'react-router-dom'

import { fields } from './page-config'
import { ROOT_PATH } from '../../../utils/config'
import PageHeader from '../../layout/PageHeader'
import NavigationFooter from '../../layout/NavigationFooter'

const ProfileUpdateSuccess = ({ match }) => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  const { view } = match.params
  const mapped = fields[view] || fields.defaults
  return (
    <div
      id="profile-page-main-view"
      className="pc-page-view pc-theme-default flex-rows"
    >
      <PageHeader theme="red" title={mapped.title} />
      <main
        role="main"
        style={{ backgroundImage }}
        className="pc-main padded is-relative flex-1 flex-rows text-center"
      >
        <h2 className="is-block fs22">
          <span
            aria-hidden
            className="icon-check-circled big-success-icon"
            title=""
          />
          <span className="is-block mt24">
            {mapped.label} a bien été modifié
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
  match: PropTypes.object.isRequired,
}

export default withRouter(ProfileUpdateSuccess)
