import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter, Redirect } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'

class RedirectPage extends Component {
  constructor () {
    super()
    this.state = {
      redirectTo: null,
    }
  }

  selectFirstOffer(userMediations) {
    return userMediations[0].userMediationOffers[0].id;
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.userMediations.length) {
      this.setState({
        redirectTo: `/decouverte/${this.selectFirstOffer(nextProps.userMediations)}`
      })
    }
  }

  render () {
    if (this.state.redirectTo) {
      return (<Redirect to={this.state.redirectTo}/>)
    }
    return <div />
  }
}

RedirectPage.defaultProps = {
  userMediations: []
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(state => ({
    userMediations: state.data.userMediations
  }))
)(RedirectPage)
