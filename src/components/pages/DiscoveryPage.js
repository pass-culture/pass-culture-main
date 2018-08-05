import PropTypes from 'prop-types'
import get from 'lodash.get'
import {
  closeLoading,
  requestData,
  showLoading,
  Logger,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Deck from '../Deck'
import Main from '../layout/Main'
import currentRecommendationSelector from '../../selectors/currentRecommendation'
import { recommendationNormalizer } from '../../utils/normalizers'

class DiscoveryPage extends Component {
  handleDataRequest = () => {
    const {
      dispatchCloseLoading,
      currentRecommendation,
      history,
      match: {
        params: { offerId, mediationId },
      },
      dispatchRequestData,
      dispatchShowLoading,
    } = this.props

    if (!currentRecommendation) {
      const query = [
        offerId && `offerId=${offerId}`,
        mediationId && `mediationId=${mediationId}`,
      ]
        .filter(param => param)
        .join('&')

      dispatchRequestData('PUT', `recommendations?${query}`, {
        handleSuccess: (state, action) => {
          if (get(action, 'data.length')) {
            if (!offerId) {
              const firstOfferId = get(action, 'data.0.offerId')

              if (!firstOfferId) {
                Logger.warn('first recommendation has no offer id, weird...')
              }

              const firstMediationId = get(action, 'data.0.mediationId') || ''

              history.push(`/decouverte/${firstOfferId}/${firstMediationId}`)
            }
          } else {
            dispatchCloseLoading({ isEmpty: true })
          }
        },
        normalizer: recommendationNormalizer,
      })
      dispatchShowLoading({ isEmpty: false })
    }
  }

  /*
  handleRedirectFromLoading(props) {
    const { history, mediationId, offerId, recommendations } = props
    if (
      !recommendations ||
      recommendations.length === 0 ||
      mediationId ||
      offerId
    )
      return

    const targetRecommendation = recommendations[0]
    // NOW CHOOSE AN OFFER AMONG THE ONES
    const recommendationOffers = targetRecommendation.recommendationOffers
    const chosenOffer =
      recommendationOffers &&
      recommendationOffers[
        Math.floor(Math.random() * recommendationOffers.length)
      ]

    // PUSH
    const path = getDiscoveryPath(chosenOffer, targetRecommendation.mediation)
    history.push(path)
  }
  */

  /*
  componentWillMount() {
    // this.handleRedirectFromLoading(this.props)
    // this.ensureRecommendations(this.props)
  }
  */

  /*
  componentWillReceiveProps(nextProps) {
    // this.handleRedirectFromLoading(nextProps)
    if (nextProps.offerId && nextProps.offerId !== this.props.offerId) {
      // this.ensureRecommendations(nextProps)
    }
  }
  */

  render() {
    const { backButton, isMenuOnTop } = this.props

    return (
      <Main
        backButton={backButton ? { className: 'discovery' } : null}
        handleDataRequest={this.handleDataRequest}
        footer={{ borderTop: true, onTop: isMenuOnTop }}
        name="discovery"
        noPadding
      >
        <Deck />
      </Main>
    )
  }
}

DiscoveryPage.defaultProps = {
  currentRecommendation: null,
  isMenuOnTop: false,
}

DiscoveryPage.propTypes = {
  backButton: PropTypes.bool.isRequired,
  currentRecommendation: PropTypes.object,
  dispatchCloseLoading: PropTypes.func.isRequired,
  dispatchRequestData: PropTypes.func.isRequired,
  dispatchShowLoading: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isMenuOnTop: PropTypes.bool,
  match: PropTypes.object.isRequired,
}

const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  return {
    backButton: ownProps.location.search.indexOf('to=verso') > -1,
    currentRecommendation: currentRecommendationSelector(
      state,
      offerId,
      mediationId
    ),
    isMenuOnTop: state.loading.isActive || get(state, 'loading.config.isEmpty'),
    recommendations: state.data.recommendations,
  }
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    {
      dispatchCloseLoading: closeLoading,
      dispatchRequestData: requestData,
      dispatchShowLoading: showLoading,
    }
  )
)(DiscoveryPage)
