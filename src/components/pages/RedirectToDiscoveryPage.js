import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter, Redirect } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import { getDiscoveryPath } from '../../utils/routes'

class RedirectToDiscoveryPage extends Component {
  constructor() {
    super()
    this.state = {
      redirectTo: null,
    }
  }

  handleSetRedirectTo = props => {
    const { recommendations } = props
    if (recommendations && recommendations.length === 0) {
      this.setState({
        redirectTo: '/decouverte/empty',
      })
      return
    }
    // THE BLOB HAS MAYBE A isAround VARIABLE
    // HELPING TO RETRIEVE THE AROUND
    let aroundRecommendation = recommendations.find(um => um.isAround)
    if (!aroundRecommendation) {
      // ELSE TAKE THE FIRST?
      aroundRecommendation = recommendations[0]
    }
    // NOW CHOOSE AN OFFER AMONG THE ONES
    const userMediationOffers = aroundRecommendation.userMediationOffers
    const chosenOffer =
      userMediationOffers &&
      userMediationOffers[
        Math.floor(Math.random() * userMediationOffers.length)
      ]
    // BUILD THE URL NOW
    this.setState({
      redirectTo: getDiscoveryPath(chosenOffer, aroundRecommendation.mediation),
    })
  }

  componentWillMount() {
    this.handleSetRedirectTo(this.props)
  }

  componentWillReceiveProps(nextProps) {
    if (
      nextProps.recommendations &&
      nextProps.recommendations !== this.props.recommendations
    ) {
      this.handleSetRedirectTo(nextProps)
    }
  }

  render() {
    if (this.state.redirectTo) {
      return <Redirect to={this.state.redirectTo} />
    }
    return <div />
  }
}

RedirectToDiscoveryPage.defaultProps = {
  recommendations: [],
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter,
  connect(state => ({
    recommendations: state.data.recommendations,
  }))
)(RedirectToDiscoveryPage)
