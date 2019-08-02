import PropTypes from 'prop-types'
import React from 'react'

import { formatRecommendationDates } from '../../../../../utils/date/date'
import { ICONS_URL } from '../../../../../utils/config'

const DEFAULT_THUMB_URL = `${ICONS_URL}/magnify.svg`

const RecommendationItem = ({
  handleMarkSearchRecommendationsAsClicked,
  offer,
  recommendation,
}) => {
  const { thumbUrl } = recommendation
  const { dateRange, name: offerName, offerType, venue } = offer || {}

  return (
    <li className="recommendation-list-item">
      <div
        className="to-details"
        onClick={handleMarkSearchRecommendationsAsClicked}
        onKeyPress={handleMarkSearchRecommendationsAsClicked}
        role="button"
        tabIndex={0}
      >
        <hr className="dotted-top-primary" />
        <div className="flex-columns">
          <div className="image flex-0 dotted-right-primary flex-rows flex-center">
            <img
              alt=""
              src={thumbUrl || DEFAULT_THUMB_URL}
            />
          </div>
          <div className="m18 flex-1">
            <h5
              className="fs18 is-bold"
              title={offerName}
            >
              {offerName}
            </h5>
            <div className="fs13">{offerType.appLabel}</div>
            <div
              className="fs13"
              id="recommendation-date"
            >
              {offer && formatRecommendationDates(venue.departementCode, dateRange)}
            </div>
          </div>
          <div className="flex-center items-center is-primary-text">
            <span
              aria-hidden
              className="icon-legacy-next"
              title=""
            />
          </div>
        </div>
      </div>
    </li>
  )
}

RecommendationItem.propTypes = {
  handleMarkSearchRecommendationsAsClicked: PropTypes.func.isRequired,
  offer: PropTypes.shape().isRequired,
  recommendation: PropTypes.shape().isRequired,
}

export default RecommendationItem
