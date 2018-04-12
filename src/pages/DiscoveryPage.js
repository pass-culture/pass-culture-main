import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import MenuButton from '../components/layout/MenuButton'
import UserMediationsDeck from '../components/UserMediationsDeck'
import withLogin from '../hocs/withLogin'
import { assignData } from '../reducers/data'
import { getContentFromUserMediation } from '../utils/content'
import { debug } from '../utils/logguers'
import { worker } from '../workers/dexie/register'
import { getDiscoveryPath } from '../utils/routes'

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
    const { history,
      userMediations
    } = this.props
    const { aroundIndex } = this.state
    isDebug && debug(`DiscoveryPage - handleUserMediationChange userMediation.id=${userMediation.id} aroundIndex=${aroundIndex}`)
    // we can replace the url but only when
    // there is an aroundIndex and we just shift for the first time
    // we already went here one time, so we can set aroundIndex to false
    // to make it not taken in account in the child Deck
    if (aroundIndex === false ||
      (aroundIndex !== null && userMediations[aroundIndex].id !== id)
    ) {
      const aroundContent = getContentFromUserMediation(userMediation)
      isDebug && debug(`DiscoveryPage - handleUserMediationChange replace`)
      // replace
      history.replace(getDiscoveryPath(aroundContent.chosenOffer, mediation))
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
      console.warn('We should have an offerId here at least')
      return
    }
    // FIND THE CORRESPONDING AROUND INDEX
    // GIVEN THE LOCAL DATA
    aroundIndex = null
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
    // IF WE FAILED TO FIND THE AROUND INDEX IN THE LOCAL
    // IT MEANS WE NEED TO ASK THE BACKEND
    if (aroundIndex === null && !hasPushPullRequested) {
      isDebug && debug(`DEBUG: DiscoveryPage - handleUserMediationRequest pushPull`)
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: null, mediationId, offerId }})
      this.hasPushPullRequested = true
      history.replace('/decouverte')
      return
    }
    isDebug && debug(`DEBUG: DiscoveryPage - handleUserMediationRequest aroundIndex=${aroundIndex}`)
    // update
    this.setState({ aroundIndex, userMediations })
  }

  componentWillMount () {
    this.handleUserMediationRequest(this.props)
  }

  componentWillReceiveProps (nextProps) {
    if (nextProps.userMediations !== this.props.userMediations) {
      this.handleUserMediationRequest(nextProps)
    }

    if (nextProps.deprecatedUserMediations && nextProps.deprecatedUserMediations !== this.props.deprecatedUserMediations) {
      nextProps.history.push('/decouverte')
      const newData = { deprecatedUserMediations: null }
      if (nextProps.userMediations.length) {
        newData.userMediations = [
          Object.assign({ isLoading: true, isRebootLoading: true }, nextProps.userMediations[0])
        ].concat(nextProps.userMediations.slice(1))
      }
      nextProps.assignData(newData)
    }
  }

  render () {
    return (
      <main className='page discovery-page center'>
        <UserMediationsDeck {...this.state}
          handleUserMediationChange={this.handleUserMediationChange} >
        </UserMediationsDeck>
        <MenuButton borderTop />
      </main>
    )
  }
}

DiscoveryPage.defaultProps = {
  // isDebug: true
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter,
  connect(state => ({
    deprecatedUserMediations: state.data.deprecatedUserMediations,
    userMediations: state.data.userMediations
  }), { assignData })
)(DiscoveryPage)
