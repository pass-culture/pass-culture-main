import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { getQueryURL } from '../../../helpers'
import { recommendationNormalizer } from '../../../utils/normalizers'
import { getRecommendationDateString } from './utils'

export class SearchResultItem extends Component {
  onSuccessLoadRecommendationDetails = () => {
    const { history, location, recommendation } = this.props
    const offerId = recommendation && recommendation.offerId
    const mediationId = recommendation && recommendation.mediationId
    const queryURL = getQueryURL({ mediationId, offerId })
    const linkURL = `${location.pathname}/item/${queryURL}${location.search}`

    history.push(linkURL)
  }

  markSearchRecommendationsAsClicked = () => {
    const { dispatch, recommendation } = this.props
    const config = {
      apiPath: `/recommendations/${recommendation.id}`,
      body: { isClicked: true },
      handleSuccess: this.onSuccessLoadRecommendationDetails,
      method: 'PATCH',
      normalizer: recommendationNormalizer,
    }

    dispatch(requestData(config))
  }

  render() {
    const { recommendation } = this.props

    return (
      <li className="recommendation-list-item">
        <div
          className="to-details"
          onClick={this.markSearchRecommendationsAsClicked}
          onKeyPress={this.markSearchRecommendationsAsClicked}
          role="button"
          tabIndex={0}
        >
          <hr className="dotted-top-primary" />
          <div className="flex-columns">
            <div className="image flex-0 dotted-right-primary flex-rows flex-center">
              <img src={recommendation.thumbUrl} alt="" />
            </div>
            <div className="m18 flex-1">
              {recommendation.offer && (
                <Fragment>
                  <h5
                    className="fs18 is-bold"
                    title={recommendation.offer.name}
                  >
                    <Dotdotdot clamp="2">{recommendation.offer.name}</Dotdotdot>
                  </h5>
                  <div className="fs13">
                    {recommendation.offer.product.offerType.appLabel}
                  </div>
                  <div id="recommendation-date" className="fs13">
                    {recommendation.offer &&
                      getRecommendationDateString(recommendation.offer)}
                  </div>
                </Fragment>
              )}
            </div>
            <div className="flex-center items-center is-primary-text">
              <span aria-hidden className="icon-legacy-next" title="" />
            </div>
          </div>
        </div>
      </li>
    )
  }
}

SearchResultItem.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  recommendation: PropTypes.shape().isRequired,
}

export default compose(
  withRouter,
  connect()
)(SearchResultItem)
