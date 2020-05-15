import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon/Icon'

const noOp = () => false

const SignoutLink = ({ historyPush, onSignOutClick, readRecommendations }) => (
  <Link
    onClick={onSignOutClick(historyPush, readRecommendations)}
    to={noOp}
  >
    <Icon svg="ico-signout" />
    <div className="list-link-label">
      {'Déconnexion'}
    </div>
  </Link>
)

SignoutLink.propTypes = {
  historyPush: PropTypes.func.isRequired,
  onSignOutClick: PropTypes.func.isRequired,
  readRecommendations: PropTypes.PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default SignoutLink
