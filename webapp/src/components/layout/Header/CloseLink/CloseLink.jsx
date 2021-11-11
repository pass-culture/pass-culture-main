import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Icon from '../../Icon/Icon'

const CloseLink = ({ actionOnClick, closeTitle, closeTo }) => (
  <Link
    className="close-link"
    onClick={actionOnClick}
    to={closeTo}
  >
    <Icon
      alt={closeTitle}
      className="close-link-img"
      svg="ico-close-white"
    />
  </Link>
)

CloseLink.defaultProps = {
  actionOnClick: null,
  closeTitle: 'Fermer',
  closeTo: '/',
}

CloseLink.propTypes = {
  actionOnClick: PropTypes.func,
  closeTitle: PropTypes.string,
  closeTo: PropTypes.string,
}

export default CloseLink
