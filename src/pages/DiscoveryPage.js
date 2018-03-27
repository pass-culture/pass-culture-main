import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import UserMediationsDeck from '../components/UserMediationsDeck'
import withLogin from '../hocs/withLogin'
import { getContentFromUserMediation } from '../utils/content'
import { debug } from '../utils/logguers'
import { worker } from '../workers/dexie/register'


class DiscoveryPage extends Component {
  constructor () {
    super()
    this.state = { aroundIndex: null,
      userMediations: null
    }
  }
  handleUserMediationChange = userMediation => {
    if (!userMediation) {
      console.warn('userMediation is not defined')
      return
    }
    const { isDebug } = this.props
    const { id, mediation } = userMediation
    const { match: { params: { offerId } },
      history,
      userMediations
    } = this.props
    const { aroundIndex } = this.state
    isDebug && debug(`DiscoveryPage - handleUserMediationChange userMediation.id=${userMediation.id} aroundIndex=${aroundIndex}`)

    // TODO: remove the case where there is no offerId since it is handled at router level

    // we can replace the url but only when
    // there is not yet an offer id (from a /decouverte just onboarding)
    // there is an aroundIndex and we just shift for the first time
    // we already went here one time, so we can set aroundIndex to false
    // to make it not taken in account in the child Deck
    if (!offerId ||
      aroundIndex === false ||
      (aroundIndex !== null && userMediations[aroundIndex].id !== id)
    ) {
      const aroundContent = getContentFromUserMediation(userMediation)
      let url = `/decouverte/${aroundContent.chosenOffer.id}`
      if (mediation) {
        url = `${url}/${mediation.id}`
      }
      isDebug && debug(`DiscoveryPage - handleUserMediationChange replace`)
      // replace
      console.log('goto', url)
      history.replace(url)
      this.setState({ aroundIndex: false })
    }
  }
  handleUserMediationRequest = props => {
    // unpack and check
    const { hasPushPullRequested } = this
    const { history,
      isDebug,
      match: { params: { mediationId, offerId } },
      userMediations
    } = props
    let { aroundIndex } = this.state
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
    isDebug && debug(`DiscoveryPage - handleUserMediationRequest offerId=${offerId}`)
    // offer not specified
    if (!offerId) {
      aroundIndex = 0
    } else {
      // null
      aroundIndex = null
      // find the matching um in the dexie buffer
      if (!mediationId) {
        userMediations.find((um, index) => {
          if (um.userMediationOffers && um.userMediationOffers.find(umo => umo.id === offerId)) {
            aroundIndex = index
            return true
          }
          return false
        })
      } else {
        userMediations.find((um, index) => {
          if (um.mediationId === mediationId) {
            aroundIndex = index
            return true
          }
          return false
        })
      }
      // we need to request around it then
      if (aroundIndex === null && !hasPushPullRequested) {
        isDebug && debug(`DEBUG: DiscoveryPage - handleUserMediationRequest pushPull`)
        worker.postMessage({ key: 'dexie-push-pull',
          state: { around: null, mediationId, offerId }})
        this.hasPushPullRequested = true
        history.replace('/decouverte')
        return
      }
    }
    isDebug && debug(`DEBUG: DiscoveryPage - handleUserMediationRequest aroundIndex=${aroundIndex}`)
    // update
    this.setState({ aroundIndex, userMediations })
  }
  handleUserMediationSuccess = props => {
    // unpack and check
    const { history,
      isDebug,
      match: { params: { offerId } },
      userMediations
    } = props
    if (!offerId) {
      const aroundUserMediation = userMediations.find(um => um.isAround)
      if (!aroundUserMediation) {
        history.replace('/decouverte')
        return
      }
      const aroundContent = getContentFromUserMediation(aroundUserMediation)
      if (!aroundContent) return;
      let url = `/decouverte/${aroundContent.chosenOffer.id}`
      if (aroundContent.mediation) {
        url = `${url}/${aroundContent.mediation.id}`
      }
      isDebug && debug(`DiscoveryPage - handleUserMediationSuccess replace`)
      // replace
      history.replace(url)
    }
  }
  onProfileClick = event => {
    this.props.history.push('/profile')
  }
  componentWillMount () {
    this.handleUserMediationRequest(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.userMediations !== this.props.userMediations) {
      this.handleUserMediationRequest(nextProps)
      this.handleUserMediationSuccess(nextProps)
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
          handleUserMediationChange={this.handleUserMediationChange} >
          <button className='discovery-page__profile'
            onClick={this.onProfileClick}
            style={{ backgroundImage: "url('../icons/pc_small.jpg')" }} />
        </UserMediationsDeck>
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
