import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import UserMediationsDeck from '../components/UserMediationsDeck'
import withLogin from '../hocs/withLogin'
import { worker } from '../workers/dexie/register'

class DiscoveryPage extends Component {
  constructor () {
    super()
    this.state = { aroundIndex: null,
      hasPushPullRequested: false
    }
  }
  handleUserMediationRequest = props => {
    // unpack and check
    const { isDebug,
      match: { params: { mediationId, offerId } },
      userMediations
    } = props
    let { aroundIndex, hasPushPullRequested } = this.state
    // no need to compute when there is no um
    // or if we have already computed once, no need to continue
    // again and again because UserMediationsDeck is taking over
    // the sync of aroundIndex
    if (!userMediations) {
      return
    } else if (aroundIndex || aroundIndex === false) {
      this.setState({ userMediations })
      return
    }
    isDebug && console.log(`DEBUG: DiscoveryPage - handleUserMediationRequest offerId=${offerId}`)
    // offer not specified
    if (!offerId) {
      aroundIndex = 0
    } else {
      // find the matching um in the dexie buffer
      if (!mediationId) {
        userMediations.find((um, index) => {
          if (um.userMediationOffers.find(umo => umo.id === offerId)) {
            aroundIndex = index
            return true
          }
        })
      } else {
        userMediations.find((um, index) => {
          if (um.mediationId === mediationId) {
            aroundIndex = index
            return true
          }
        })
      }
      // we need to request around it then
      if (!aroundIndex && !hasPushPullRequested) {
        isDebug && console.log(`DEBUG: DiscoveryPage - handleUserMediationRequest pushPull`)
        worker.postMessage({ key: 'dexie-push-pull',
          state: { around: null, mediationId, offerId }})
        this.setState({ hasPushPullRequested: true })
        return
      }
    }
    isDebug && console.log(`DEBUG: DiscoveryPage - handleUserMediationRequest aroundIndex=${aroundIndex}`)
    // update
    this.setState({ aroundIndex, userMediations })
  }
  handleUserMediationChange = userMediation => {
    if (!userMediation) {
      console.warn('userMediation is not defined')
      return
    }
    const { isDebug } = this.props
    const { id, mediation, userMediationOffers } = userMediation
    const { match: { params: { offerId } },
      history,
      userMediations
    } = this.props
    const { aroundIndex } = this.state
    isDebug && console.log(`DEBUG: DiscoveryPage - handleUserMediationChange userMediation.id=${userMediation.id} aroundIndex=${aroundIndex}`)
    // we can replace the url but only when
    // there is not yet an offer id (from a /decouverte just onboarding)
    // there is an aroundIndex and we just shift for the first time
    // we already went here one time, so we can set aroundIndex to false
    // to make it not taken in account in the child Deck
    if (!offerId ||
      aroundIndex === false ||
      (aroundIndex !== null && userMediations[aroundIndex].id !== id)
    ) {
      let url = `/decouverte/${userMediationOffers[0].id}`
      if (mediation) {
        url = `${url}/${mediation.id}`
      }
      isDebug && console.log(`DEBUG: DiscoveryPage - handleUserMediationChange replace`)
      // replace
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
    // console.log('RENDER: DiscoveryPage this.state.userMediations', this.state.userMediations && this.props.userMediations.length,
    //  this.state.userMediations && this.state.userMediations.map(um =>
    //    um && `${um.id} ${um.dateRead}`))
    // console.log('RENDER: DiscoveryPage this.state.aroundIndex', this.state.aroundIndex)
    return (
      <main className='page discovery-page center'>
        <UserMediationsDeck {...this.state}
          handleUserMediationChange={this.handleUserMediationChange}
          isBlobModel />
      </main>
    )
  }
}

DiscoveryPage.defaultProps = {
  // isDebug: true
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(state => ({ userMediations: state.data.userMediations }))
)(DiscoveryPage)
