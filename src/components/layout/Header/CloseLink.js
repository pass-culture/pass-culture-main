import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Icon from '../Icon'

const CloseLink = ({ actionOnClick, closeTitle, closeTo }) => (
  <Link className="close-link" onClick={actionOnClick} to={closeTo}>
    <Icon alt={closeTitle} className="close-link-img" svg="ico-close" />
  </Link>
)

CloseLink.defaultProps = {
  actionOnClick: null,
  closeTitle: 'Retourner à la page découverte',
  closeTo: '/decouverte',
}

CloseLink.propTypes = {
  actionOnClick: PropTypes.func,
  closeTitle: PropTypes.string,
  closeTo: PropTypes.string,
}

export default CloseLink
