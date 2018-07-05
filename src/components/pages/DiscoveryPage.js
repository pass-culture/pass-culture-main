import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Deck from '../Deck'
import PageWrapper from '../layout/PageWrapper'
import withLogin from '../hocs/withLogin'
import { requestData } from '../../reducers/data'
import selectCurrentRecommendation from '../../selectors/currentRecommendation'
import { getDiscoveryPath } from '../../utils/routes'

class DiscoveryPage extends Component {
  handleSetRedirectTo(nextProps) {
    // ONLY TRIGGER AT MOUNT TIME
    // OR WHEN WE RECEIVED FRESH NON EMPTY DATA
    const props = nextProps || this.props
    const { currentRecommendation, occasionId, mediationId, offerId, history, recommendations, requestData } = props
    if (
      offerId !== 'empty' ||
      (nextProps && !nextProps.recommendations) ||
      (offerId !== 'empty' || !recommendations || !recommendations.length)
    ) {
      if (!currentRecommendation) {
        let query = 'occasionType=Event'
        if (mediationId) {
          query += '&mediationId='+mediationId
        }
        query += '&occasionId='+occasionId
        requestData('PUT', 'recommendations?'+query)
      }
     return
    }

    // THE BLOB HAS MAYBE A isAround VARIABLE
    // HELPING TO RETRIEVE THE AROUND
    let targetRecommendation = recommendations.find(um => um.isAround)
    if (!targetRecommendation) {
      // ELSE TAKE THE FIRST?
      targetRecommendation = recommendations[0]
    }

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
    this.handleSetRedirectTo()
  }

  componentWillReceiveProps(nextProps) {
    this.handleSetRedirectTo(nextProps)
  }

  render() {
    return (
      <PageWrapper
        name="discovery"
        noPadding
        menuButton={{ borderTop: true }}
        backButton={this.props.backButton ? { className: 'discovery' } : null}
      >
        <Deck />
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter,
  connect(state => ({
    backButton: state.router.location.search.indexOf('to=verso') > -1,
    currentRecommendation: selectCurrentRecommendation(state),
    occasionId: state.router.location.hash,
    recommendations: state.data.recommendations,
  }), { requestData })
)(DiscoveryPage)
