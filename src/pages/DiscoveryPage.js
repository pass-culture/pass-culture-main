import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import UserMediationsDeck from '../components/UserMediationsDeck'
import withLogin from '../hocs/withLogin'
import { worker } from '../workers/dexie'

class DiscoveryPage extends Component {
  constructor () {
    super()
    this.state = { aroundIndex: null }
  }
  handleUserMediationRequest = props => {
    // unpack and check
    const { match: { params: { mediationId, offerId } },
      requestData,
      userMediations
    } = props
    if (!userMediations) {
      return
    }
    // find the matching um in the dexie buffer
    let aroundIndex
    if (!mediationId) {
      userMediations.find((um, index) => {
        aroundIndex = index
        return um.userMediationOffers.find(umo => umo.id === offerId)
      })
    } else {
      userMediations.find((um, index) => {
        aroundIndex = index
        return um.mediationId === mediationId
      })
    }
    const userMediation = userMediations[aroundIndex]
    // we need to request around him then
    if (!userMediation) {
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: userMediation.id }})
    }
    this.setState({ aroundIndex })
  }
  handleUserMediationChange = userMediation => {
    const { id, mediation, userMediationOffers } = userMediation
    const { match: { params: { offerId } },
      history,
      userMediations
    } = this.props
    const { aroundIndex } = this.state
    // we can replace the url but not when
    // there is not yet an offer id (from a /decouverte just onboarding)
    // there is an aroundIndex but the deck just init with a not correct matching id
    // when we already went here one time, so we can set aroundIndex to false
    // to make it not taken in account in the child Deck
    if (!offerId ||
      (aroundIndex && userMediations[aroundIndex].id === id) ||
      aroundIndex === false
    ) {
      let url = `/decouverte/${userMediationOffers[0].id}`
      if (mediation) {
        url = `${url}/${mediation.id}`
      }
      history.replace(url)
      this.setState({ aroundIndex: false })
    }
  }
  componentWillMount () {
    this.handleUserMediationRequest(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.userMediations !== this.props.userMediations) {
      this.handleUserMediationRequest(nextProps)
    }
  }
  render () {
    return (
      <main className='page discovery-page center'>
        <UserMediationsDeck {...this.state}
          handleUserMediationChange={this.handleUserMediationChange}
          isBlobModel/>
      </main>
    )
  }
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(state => ({ userMediations: state.data.userMediations }))
)(DiscoveryPage)
