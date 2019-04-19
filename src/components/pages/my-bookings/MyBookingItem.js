/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import Thumb from '../../layout/Thumb'
import Ribbon from '../../layout/Ribbon'
import { getQueryURL } from '../../../helpers'

const MyBookingItem = ({
  completedUrl,
  date,
  dateString,
  isCancelled,
  isEvent,
  mediationId,
  name,
  offerId,
  timezone,
  recommendation,
  token,
}) => {
  const cssclass = (isEvent && 'event') || 'thing'
  const queryURL = getQueryURL({ mediationId, offerId })
  const linkURL = `/decouverte/${queryURL}/verso`
  return (
    <li
      data-token={token}
      data-booked-date={date}
      data-booked-timezone={timezone}
      className={`booking-item mb16 ${cssclass}`}
    >
      {isCancelled && <Ribbon />}
      <Link to={linkURL}>
        <Thumb src={recommendation.thumbUrl} />
        <div className="infos">
          <div className="top">
            <h5 title={name} className="fs18 is-semi-bold">
              <Dotdotdot clamp={date ? 2 : 3}>{name}</Dotdotdot>
            </h5>
            <span className="fs13">{dateString || 'permanent'}</span>
          </div>
          {!completedUrl && <div className="token">{token}</div>}
        </div>
        <div className="arrow">
          <Icon svg="ico-next-S" className="Suivant" />
        </div>
      </Link>
    </li>
  )
}

MyBookingItem.defaultProps = {
  completedUrl: null,
  date: null,
  dateString: null,
  isCancelled: false,
  isEvent: false,
  mediationId: null,
  name: null,
  offerId: null,
  recommendation: {},
  token: null,
}

MyBookingItem.propTypes = {
  completedUrl: PropTypes.string,
  date: PropTypes.string,
  dateString: PropTypes.string,
  isCancelled: PropTypes.bool,
  isEvent: PropTypes.bool,
  mediationId: PropTypes.string,
  name: PropTypes.string,
  offerId: PropTypes.string,
  recommendation: PropTypes.shape(),
  timezone: PropTypes.string.isRequired,
  token: PropTypes.string,
}

export default MyBookingItem
