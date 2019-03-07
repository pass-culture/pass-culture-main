/* eslint
  react/jsx-one-expression-per-line: 0 */
// import { requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import Dotdotdot from 'react-dotdotdot'

import { getQueryURL } from '../../../helpers'
import { getRecommendationDateString } from './utils'
// import { recommendationNormalizer } from '../../../utils/normalizers'

class RawSearchResultItem extends Component {
  /*
  handleClickRecommendation = recommendation => {
    if (recommendation.isClicked) {
      return
    }

    const { dispatch } = this.props
    const options = {
      body: { isClicked: true },
      key: 'recommendations',
    }

    const path = `recommendations/${recommendation.id}`

    dispatch(requestData('PATCH', path, options))
  }
  */

  handleRedirectToItem = () => {
    const { history, location, recommendation } = this.props
    const offerId = recommendation && recommendation.offerId
    const mediationId = recommendation && recommendation.mediationId
    const queryURL = getQueryURL({ mediationId, offerId })
    const linkURL = `${location.pathname}/item/${queryURL}${location.search}`
    history.push(linkURL)
  }

  /*
  handleRequestSuccess = (state, action) => {
    this.handleClickRecommendation(action.data)
    this.handleRedirectToItem()
  }

  onItem = () => {
    const { dispatch, recommendation } = this.props
    const offerId = recommendation && recommendation.offerId
    const mediationId = recommendation && recommendation.mediationId

    let path = `recommendations/offers/${offerId}`
    if (mediationId) {
      path = `${path}?mediationId=${mediationId}`
    }

    dispatch(
      requestData('GET', path, {
        handleSuccess: this.handleRequestSuccess,
        normalizer: recommendationNormalizer,
      })
    )
  }
  */

  render() {
    const { recommendation } = this.props

    return (
      <li className="recommendation-list-item">
        <div
          className="to-details"
          onClick={
            // this.onItem
            this.handleRedirectToItem
          }
          onKeyPress={
            // this.onItem
            this.handleRedirectToItem
          }
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
  // dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  recommendation: PropTypes.object.isRequired,
}

export default RawSearchResultItem
