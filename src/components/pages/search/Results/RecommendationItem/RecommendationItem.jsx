import PropTypes from 'prop-types'
import React from 'react'

import { formatRecommendationDates } from '../../../../../utils/date/date'
import { ICONS_URL } from '../../../../../utils/config'

const DEFAULT_THUMB_URL = `${ICONS_URL}/picto-placeholder-visueloffre.png`

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
        <div className="search-result-item-container">
          <div className="image">
            <img
              alt=""
              src={thumbUrl || DEFAULT_THUMB_URL}
            />
          </div>
          <div className="search-result-item-detail">
            <h5 title={offerName}>{offerName}</h5>
            <div className="search-result-item-type">{offerType.appLabel}</div>
            <div
              className="search-result-item-date"
              id="recommendation-date"
            >
              {offer && formatRecommendationDates(venue.departementCode, dateRange)}
            </div>
          </div>
          <div className="arrow-container">
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
