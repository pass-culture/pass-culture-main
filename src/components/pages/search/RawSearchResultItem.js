/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { requestData } from 'redux-saga-data'

import { getQueryURL } from '../../../helpers'
import { getRecommendationDateString } from './utils'
import { recommendationNormalizer } from '../../../utils/normalizers'

class RawSearchResultItem extends Component {
  handleRequestSuccess = () => {
    const { history, location, recommendation } = this.props
    const offerId = recommendation && recommendation.offerId
    const mediationId = recommendation && recommendation.mediationId
    const queryURL = getQueryURL({ mediationId, offerId })
    const linkURL = `${location.pathname}/item/${queryURL}${location.search}`
    history.push(linkURL)
  }

  onClickRecommendation = () => {
    const { dispatch, recommendation } = this.props

    const config = {
      apiPath: `/recommendations/${recommendation.id}`,
      body: { isClicked: true },
      handleSuccess: this.handleRequestSuccess,
      key: 'recommendations',
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
          onClick={this.onClickRecommendation}
          onKeyPress={this.onClickRecommendation}
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
          </div>
        </div>
      </li>
    )
  }
}

RawSearchResultItem.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  recommendation: PropTypes.object.isRequired,
}

export default RawSearchResultItem
