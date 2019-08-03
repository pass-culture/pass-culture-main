import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon'
import Ribbon from '../../../layout/Ribbon'

const MyBooking = ({
  name,
  ribbon,
  stringifyDate,
  thumbUrl,
  token,
  versoUrl,
}) => (
  <li
    className="mb-my-booking"
    data-token={token}
  >
    <Link
      className="teaser-link"
      to={versoUrl}
    >
      <div className="teaser-thumb">{thumbUrl && <img
        alt=""
        src={thumbUrl}
                                                 />}
      </div>
      <div className="teaser-wrapper">
        <div className="mb-heading">
          <div className="teaser-title">{name}</div>
          <div className="teaser-sub-title">{stringifyDate}</div>
        </div>
        <div className="mb-token">{token}</div>
      </div>
      <div className="teaser-arrow">
        {ribbon &&
          <Ribbon
            label={ribbon.label}
            type={ribbon.type}
          />}
        <Icon
          className="teaser-arrow-img"
          svg="ico-next-S"
        />
      </div>
    </Link>
  </li>
)

MyBooking.defaultProps = {
  ribbon: null,
  thumbUrl: null,
}

MyBooking.propTypes = {
  name: PropTypes.string.isRequired,
  ribbon: PropTypes.shape(),
  stringifyDate: PropTypes.string.isRequired,
  thumbUrl: PropTypes.string,
  token: PropTypes.string.isRequired,
  versoUrl: PropTypes.string.isRequired,
}

export default MyBooking
