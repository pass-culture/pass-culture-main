import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Deck from '../client/Deck'
import MenuButton from '../client/MenuButton'
import withLogin from '../hocs/withLogin'
import { getDiscoveryPath } from '../../utils/routes'

class DiscoveryPage extends Component {
  handleSetRedirectTo(nextProps) {
    // ONLY TRIGGER AT MOUNT TIME
    // OR WHEN WE RECEIVED FRESH NON EMPTY DATA
    const props = nextProps || this.props
    const { offerId, history, recommendations } = props
    if (
      offerId !== 'empty' ||
      (nextProps && !nextProps.recommendations) ||
      (offerId !== 'empty' || !recommendations || !recommendations.length)
    ) {
      return
    }

    // THE BLOB HAS MAYBE A isAround VARIABLE
    // HELPING TO RETRIEVE THE AROUND
    let currentRecommendation = recommendations.find(um => um.isAround)
    if (!currentRecommendation) {
      // ELSE TAKE THE FIRST?
      currentRecommendation = recommendations[0]
    }

    // NOW CHOOSE AN OFFER AMONG THE ONES
    const userMediationOffers = currentRecommendation.userMediationOffers
    const chosenOffer =
      userMediationOffers &&
      userMediationOffers[
        Math.floor(Math.random() * userMediationOffers.length)
      ]

    // PUSH
    const path = getDiscoveryPath(chosenOffer, currentRecommendation.mediation)
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
      <main className="page discovery-page center">
        <Deck />
        <MenuButton borderTop />
      </main>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter,
  connect(state => ({ recommendations: state.data.recommendations }))
)(DiscoveryPage)
