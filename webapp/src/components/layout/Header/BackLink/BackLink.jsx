import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../Icon/Icon'

const BackLink = ({ actionOnClick, backTitle, backTo }) => (
  <Link
    className="back-link"
    onClick={actionOnClick}
    to={backTo}
  >
    <Icon
      alt={backTitle}
      className="close-link-img"
      svg="ico-back"
    />
  </Link>
)

BackLink.defaultProps = {
  actionOnClick: null,
  backTitle: 'Retour',
}

BackLink.propTypes = {
  actionOnClick: PropTypes.func,
  backTitle: PropTypes.string,
  backTo: PropTypes.string.isRequired,
}

export default BackLink
