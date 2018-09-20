/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import moment from 'moment'
import { capitalize } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import { getQueryURL } from '../../../helpers'
import { getTimezone } from '../../../utils/timezone'

const formatDate = (date, tz) =>
  capitalize(
    moment(date)
      .tz(tz)
      .format('dddd DD/MM/YYYY')
  )

const getRecommendationDateString = (offer, tz) => {
  if (offer.eventId === null) return 'permanent'
  const fromDate = offer.dateRange[0]
  const toDate = offer.dateRange[1]
  const formatedDate = `du
  ${formatDate(fromDate, tz)} au ${formatDate(toDate, tz)}`
  return formatedDate
}

const SearchResultItem = ({ recommendation }) => {
  const offerId = get(recommendation, 'offerId')
  const mediationId = get(recommendation, 'mediationId')
  const departementCode = get(recommendation, 'offer.venue.departementCode')
  const tz = getTimezone(departementCode)

  const queryURL = getQueryURL({ mediationId, offerId })
  const linkURL = `/decouverte/${queryURL}`
  return (
    <li className="recommendation-list-item">
      <hr className="dotted-top-primary" />
      <Link to={linkURL} className="flex-columns items-center">
        <div className="image flex-0 dotted-right-primary flex-rows flex-center">
          <img src={recommendation.thumbUrl} alt="" />
        </div>
        <div className="m18 flex-1">
          {recommendation.offer && (
            <Fragment>
              <h5
                className="fs18 is-bold"
                title={recommendation.offer.eventOrThing.name}
              >
                <Dotdotdot clamp="2">
                  {recommendation.offer.eventOrThing.name}
                </Dotdotdot>
              </h5>
              <span className="fs13">
                {recommendation.offer &&
                  getRecommendationDateString(recommendation.offer, tz)}
              </span>
            </Fragment>
          )}
        </div>
        <div className="flex-0 is-primary-text">
          <span aria-hidden className="icon-next" title="" />
        </div>
      </Link>
    </li>
  )
}

SearchResultItem.propTypes = {
  recommendation: PropTypes.object.isRequired,
}

export default SearchResultItem
