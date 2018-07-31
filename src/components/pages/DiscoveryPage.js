import get from 'lodash.get'
import { closeLoading, requestData, showLoading } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Deck from '../Deck'
import Main from '../layout/Main'
import selectCurrentEventOrThingId from '../../selectors/currentEventOrThingId'
import selectCurrentRecommendation from '../../selectors/currentRecommendation'
import { recommendationNormalizer } from '../../utils/normalizers'
import { getDiscoveryPath } from '../../utils/getDiscoveryPath'

class DiscoveryPage extends Component {
  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      closeLoading,
      currentRecommendation,
      eventOrThingId,
      mediationId,
      requestData,
      showLoading,
    } = this.props
    if (!currentRecommendation) {
      let query = ''
      if (mediationId || eventOrThingId) {
        query += 'occasionType=event'
      }
      if (mediationId) {
        query += `&mediationId=${mediationId}`
      }
      if (eventOrThingId) {
        query += `&occasionId=${eventOrThingId}`
      }
      requestData('PUT', `recommendations?${  query}`, {
        handleSuccess: (state, action) => {
          if (!get(action, 'data.length')) {
            closeLoading({ isEmpty: true })
          }
        },
        normalizer: recommendationNormalizer,
      })
      showLoading({ isEmpty: false })
    }
  }

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

  componentWillMount() {
    // this.handleRedirectFromLoading(this.props)
    // this.ensureRecommendations(this.props)
  }

  componentWillReceiveProps(nextProps) {
    // this.handleRedirectFromLoading(nextProps)
    if (nextProps.offerId && nextProps.offerId !== this.props.offerId) {
      // this.ensureRecommendations(nextProps)
    }
  }

  render() {
    const { backButton, isMenuOnTop } = this.props

    return (
      <Main
        backButton={backButton ? { className: 'discovery' } : null}
        handleDataRequest={this.handleDataRequest}
        menuButton={{ borderTop: true, onTop: isMenuOnTop }}
        name="discovery"
        noPadding
      >
        <Deck />
      </Main>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({
      backButton: state.router.location.search.indexOf('to=verso') > -1,
      currentRecommendation: selectCurrentRecommendation(state),
      eventOrThingId: selectCurrentEventOrThingId(state),
      isMenuOnTop:
        state.loading.isActive || get(state, 'loading.config.isEmpty'),
      recommendations: state.data.recommendations,
    }),
    { closeLoading, requestData, showLoading }
  )
)(DiscoveryPage)
