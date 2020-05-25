import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon/Icon'

const noOp = () => false

const SignoutLink = ({
  historyPush,
  readRecommendations,
  signOut,
  resetSeedLastRequestTimestamp,
  updateReadRecommendations,
  reinitializeDataExceptFeatures,
}) => {
  const handleSignOut = () => {
    signOut(reinitializeDataExceptFeatures)
    resetSeedLastRequestTimestamp(Date.now())
    historyPush('/connexion')
  }

  const handleSignoutClick = () => () => {
    readRecommendations && readRecommendations.length > 0
      ? updateReadRecommendations(readRecommendations, handleSignOut)
      : handleSignOut()
  }

  return (
    <Link
      onClick={handleSignoutClick()}
      to={noOp}
    >
      <Icon svg="ico-signout" />
      <div className="list-link-label">
        {'Déconnexion'}
      </div>
    </Link>
  )
}

SignoutLink.propTypes = {
  historyPush: PropTypes.func.isRequired,
  readRecommendations: PropTypes.PropTypes.arrayOf(PropTypes.shape()).isRequired,
  reinitializeDataExceptFeatures: PropTypes.func.isRequired,
  resetSeedLastRequestTimestamp: PropTypes.func.isRequired,
  signOut: PropTypes.func.isRequired,
  updateReadRecommendations: PropTypes.func.isRequired,
}

export default SignoutLink
