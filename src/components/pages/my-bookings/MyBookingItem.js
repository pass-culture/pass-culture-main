/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import moment from 'moment'
import { capitalize, Icon } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import Thumb from '../../layout/Thumb'
import Ribbon from '../../layout/Ribbon'
import { getQueryURL } from '../../../helpers'
import { THUMBS_URL } from '../../../utils/config'
import { getTimezone } from '../../../utils/timezone'
import { selectRecommendation } from '../../../selectors'

// TODO A tester
const getDateString = (date, tz) =>
  date &&
  capitalize(
    moment(date)
      .tz(tz)
      .format('dddd DD/MM/YYYY à H:mm')
  )

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
  token,
}) => {
  const cssclass = (isEvent && 'event') || 'thing'
  const queryURL = getQueryURL({ mediationId, offerId })
  const linkURL = `/decouverte/${queryURL}/verso`
  const thumbUrl = `${THUMBS_URL}/mediations/${mediationId}`
  return (
    <li
      data-token={token}
      data-booked-date={date}
      data-booked-timezone={timezone}
      className={`booking-item mb16 ${cssclass}`}
    >
      {isCancelled && <Ribbon />}
      <Link to={linkURL}>
        <Thumb src={thumbUrl} />
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
  timezone: PropTypes.string.isRequired,
  token: PropTypes.string,
}

export default connect((state, ownProps) => {
  const { booking } = ownProps || {}
  const { isCancelled, recommendationId, stock, token } = booking
  const completedUrl = get(booking, 'completedUrl')
  const offerId = get(stock, 'resolvedOffer.id')
  const name = get(stock, 'resolvedOffer.eventOrThing.name')
  const date = get(stock, 'eventOccurrence.beginningDatetime')
  const departementCode = get(stock, 'resolvedOffer.venue.departementCode')
  const timezone = getTimezone(departementCode)
  const dateString = getDateString(date, timezone)

  const recommendation = selectRecommendation(state, recommendationId)
  const mediationId = get(recommendation, 'mediationId')

  const isEvent = Boolean(get(stock, 'resolvedOffer.eventId'))

  // injected
  return {
    completedUrl,
    date,
    dateString,
    isCancelled,
    isEvent,
    mediationId,
    name,
    offerId,
    recommendation,
    timezone,
    token,
  }
})(MyBookingItem)
