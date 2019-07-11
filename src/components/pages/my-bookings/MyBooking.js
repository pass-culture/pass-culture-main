import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../layout/Icon'
import Ribbon from '../../layout/Ribbon'

const MyBooking = ({
  isCancelled,
  name,
  offerVersoUrl,
  stringifyDate,
  thumbUrl,
  token,
}) => (
  <li
    className="mb-my-booking"
    data-token={token}
  >
    <Link
      className="mb-link"
      to={offerVersoUrl}
    >
      <div className="mb-thumb">
        {thumbUrl && <img
          alt=""
          src={thumbUrl}
                     />}
      </div>
      <div className="mb-infos">
        <div className="mb-heading">
          <div className="mb-title">{name}</div>
          <div className="mb-date">{stringifyDate}</div>
        </div>
        <div className="mb-token">{token}</div>
      </div>
      <div className="mb-arrow">
        {isCancelled && <Ribbon />}
        <Icon
          className="mb-arrow-img"
          svg="ico-next-S"
        />
      </div>
    </Link>
  </li>
)

MyBooking.defaultProps = {
  isCancelled: false,
  stringifyDate: 'Permanent',
  thumbUrl: null,
}

MyBooking.propTypes = {
  isCancelled: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offerVersoUrl: PropTypes.string.isRequired,
  stringifyDate: PropTypes.string,
  thumbUrl: PropTypes.string,
  token: PropTypes.string.isRequired,
}

export default MyBooking
