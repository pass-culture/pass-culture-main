import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter, Redirect } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import { getDiscoveryPath } from '../utils/routes'

class RedirectToDiscoveryPage extends Component {
  constructor () {
    super()
    this.state = {
      redirectTo: null,
    }
  }

  handleSetRedirectTo = props => {
    const { userMediations } = props
    if (!userMediations || userMediations.length === 0) {
      return
    }
    // THE BLOB HAS MAYBE A isAround VARIABLE
    // HELPING TO RETRIEVE THE AROUND
    let aroundUserMediation = userMediations.find(um => um.isAround)
    if (!aroundUserMediation) {
      // ELSE TAKE THE FIRST?
      aroundUserMediation = userMediations[0]
    }
    // NOW CHOOSE AN OFFER AMONG THE ONES
    const userMediationOffers = aroundUserMediation.userMediationOffers
    const chosenOffer = userMediationOffers &&
      userMediationOffers[Math.floor(Math.random() * userMediationOffers.length)]
    // BUILD THE URL NOW
    this.setState({
      redirectTo: getDiscoveryPath(chosenOffer, aroundUserMediation.mediation)
    })
  }

  componentWillMount () {
    this.handleSetRedirectTo(this.props)
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.userMediations && (nextProps.userMediations !== this.props.userMediations)) {
      this.handleSetRedirectTo(nextProps)
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
