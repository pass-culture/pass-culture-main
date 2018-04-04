import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter, Redirect } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'

class RedirectToDiscoveryPage extends Component {
  constructor () {
    super()
    this.state = {
      redirectTo: null,
    }
  }

  handleSelectOffer = props => {
    const { userMediations } = props
    if (!userMediations || userMediations.length === 0) {
      return
    }
    // THE BLOB HAS ALREADY A isAround VARIABLE
    // HELPING TO RETRIEVE THE AROUND
    const aroundUserMediation = userMediations.find(um => um.isAround)
    if (!aroundUserMediation) {
      // history.replace('/decouverte')
      return
    }
    // NOW CHOOSE AN OFFER AMONG THE ONES
    const userMediationOffers = aroundUserMediation.userMediationOffers
    const chosenOffer = userMediationOffers &&
      userMediationOffers[Math.floor(Math.random() * userMediationOffers.length)]
    // BUILD THE URL NOW
    let redirectTo = `/decouverte/${chosenOffer.id}`
    if (aroundUserMediation.mediation) {
      redirectTo = `${redirectTo}/${aroundUserMediation.mediation.id}`
    }
    this.setState({
      redirectTo
    })
  }

  componentWillMount () {
    this.handleSelectOffer(this.props)
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.userMediations && (nextProps.userMediations !== this.props.userMediations)) {
      this.handleSelectOffer(nextProps)
    }
  }

  render () {
    if (this.state.redirectTo) {
      return (<Redirect to={this.state.redirectTo}/>)
    }
    return <div />
  }
}

RedirectToDiscoveryPage.defaultProps = {
  userMediations: []
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter,
  connect(state => ({
    userMediations: state.data.userMediations
  }))
)(RedirectToDiscoveryPage)
