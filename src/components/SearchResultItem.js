/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import moment from 'moment'
import { capitalize, Icon } from 'pass-culture-shared'
import React from 'react'
// import { connect } from 'react-redux'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import Thumb from './layout/Thumb'
import { getQueryURL } from '../helpers'
import { THUMBS_URL } from '../utils/config'
import { getTimezone } from '../utils/timezone'
// import { selectRecommendation } from '../selectors'

const formatDate = (date, tz) =>
  capitalize(
    moment(date)
      .tz(tz)
      .format('dddd DD/MM/YYYY')
  )

const getOfferDateString = (offer, tz) => {
  if (offer.eventId === null) {
    return 'permanent'
  }
  return `du
  ${formatDate(offer.eventOrThing.dateRange[0], tz)} au ${formatDate(
    offer.eventOrThing.dateRange[1],
    tz
  )}`
}

const getOfferThumb = offer => {
  const mediationId = get(offer, 'mediation.id')
  if (mediationId) {
    return `${THUMBS_URL}/mediations/${mediationId}`
  }
  if (get(offer, 'eventId')) {
    return `${THUMBS_URL}/events/${offer.eventId}`
  }

  return `${THUMBS_URL}/things/${offer.thingId}`
}

const SearchResultItem = ({ recommendation }) => {
  const offerId = get(recommendation, 'offerId')
  const mediationId = get(recommendation, 'mediationId')
  const departementCode = get(recommendation, 'offer.venue.departementCode')
  const tz = getTimezone(departementCode)

  const queryURL = getQueryURL({ mediationId, offerId })
  const linkURL = `/decouverte/${queryURL}`

  return (
    <li className="booking-item">
      <Link to={linkURL}>
        <Thumb src={getOfferThumb(recommendation.offer)} />
        <div className="infos">
          <div className="top">
            <h5 title={recommendation.offer.eventOrThing.name}>
              <Dotdotdot clamp="2">
                {recommendation.offer.eventOrThing.name}
              </Dotdotdot>
            </h5>
            <span>{getOfferDateString(recommendation.offer, tz)}</span>
          </div>
        </div>
        <div className="arrow">
          <Icon svg="ico-next-S" className="Suivant" />
        </div>
      </Link>
    </li>
  )
}

SearchResultItem.propTypes = {
  recommendation: PropTypes.object.isRequired,
}

export default SearchResultItem
