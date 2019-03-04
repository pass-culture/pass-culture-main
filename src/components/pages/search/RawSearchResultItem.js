/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import React, { Fragment } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'

import { getQueryURL } from '../../../helpers'
import { getRecommendationDateString } from './utils'

const RawSearchResultItem = ({ location, recommendation }) => {
  const offerId = get(recommendation, 'offerId')
  const mediationId = get(recommendation, 'mediationId')
  const queryURL = getQueryURL({ mediationId, offerId })
  const linkURL = `${location.pathname}/item/${queryURL}${location.search}`

  return (
    <li className="recommendation-list-item">
      <hr className="dotted-top-primary" />
      <Link to={linkURL} className="flex-columns">
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
              <span id="recommendation-date" className="fs13">
                {recommendation.offer &&
                  getRecommendationDateString(recommendation.offer)}
              </span>
            </Fragment>
          )}
        </div>
        <div className="flex-center items-center is-primary-text">
          <span aria-hidden className="icon-legacy-next" title="" />
        </div>
      </Link>
    </li>
  )
}

RawSearchResultItem.propTypes = {
  location: PropTypes.object.isRequired,
  recommendation: PropTypes.object.isRequired,
}

export default RawSearchResultItem
