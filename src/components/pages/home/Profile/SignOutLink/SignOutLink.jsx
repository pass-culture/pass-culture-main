import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../../layout/Icon/Icon'

const noOp = () => false

const SignOutLink = ({
  historyPush,
  reinitializeDataExceptFeatures,
  resetSeedLastRequestTimestamp,
  signOut,
}) => {
  const handleSignOutClick = () => async () => {
    await signOut()

    historyPush('/connexion')
    resetSeedLastRequestTimestamp(Date.now())
    reinitializeDataExceptFeatures()
  }

  return (
    <Link
      onClick={handleSignOutClick()}
      to={noOp}
    >
      <Icon svg="ico-signout" />
      <div className="list-link-label">
        {'Déconnexion'}
      </div>
    </Link>
  )
}

SignOutLink.propTypes = {
  historyPush: PropTypes.func.isRequired,
  reinitializeDataExceptFeatures: PropTypes.func.isRequired,
  resetSeedLastRequestTimestamp: PropTypes.func.isRequired,
  signOut: PropTypes.func.isRequired,
}

export default SignOutLink
