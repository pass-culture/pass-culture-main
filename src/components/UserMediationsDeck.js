import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Deck from './Deck'
import UserMediationsDebug from './UserMediationsDebug'
import { requestData } from '../reducers/data'
import { IS_DEV } from '../utils/config'
import { getContentFromUserMediation } from '../utils/content'
import { worker } from '../workers/dexie/register'

class UserMediationsDeck extends Component {
  constructor() {
    super()
    this.state = { aroundIndex: null,
      contents: null,
      hasSyncRequested: false,
      isLoadingBefore: false,
      isLoadingAfter: false,
      isTransitioning: false
    }
  }
  handleBeforeContent = diffIndex => {
    // unpack and check
    const { countBeforeSync,
      isDebug,
      userMediations
    } = this.props
    const { aroundIndex,
      contents,
      hasSyncRequested
    } = this.state
    if (aroundIndex === null || aroundIndex < 0) {
      return
    }
    // from the present to the past
    // meet the first not well defined content
    const limit = countBeforeSync + 1
    isDebug && console.log(`DEBUG: UserMediationsDeck - handleAfterContent aroundIndex=${aroundIndex} limit=${limit}`)
    // compute
    const isBeforeSync = aroundIndex < limit
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isBeforeSync && !hasSyncRequested) {
      this.setState({ isLoadingBefore: true,
        hasSyncRequested: true })
      const beforeAroundIndex = Math.max(0, aroundIndex - diffIndex)
      const aroundUserMediation = userMediations[beforeAroundIndex]
      const aroundContent = getContentFromUserMediation(aroundUserMediation)
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: aroundContent.id }})
      return
    }
    // update
    if (hasSyncRequested) {
      this.setState({ hasSyncRequested: false })
    }
  }
  handleAfterContent = diffIndex => {
    // check unpack
    const { countAfterSync,
      isDebug,
      userMediations
    } = this.props
    const { aroundIndex,
      contents,
      hasSyncRequested
    } = this.state
    isDebug && console.log(`DEBUG: UserMediationsDeck - handleAfterContent aroundIndex=${aroundIndex}`)
    if (aroundIndex === null || aroundIndex > userMediations.length) {
      return
    }
    // from the present to the past
    // meet the first not well defined content
    const limit = userMediations.length - 1 - countAfterSync
    isDebug && console.log(`DEBUG: UserMediationsDeck - handleAfterContent aroundIndex=${aroundIndex} limit=${limit}`)
    // compute
    const isAfterSync = aroundIndex > limit
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isAfterSync && !hasSyncRequested) {
      this.setState({ isLoadingAfter: true,
        hasSyncRequested: true,
      })
      const afterAroundIndex = Math.min(userMediations.length - 1,
        aroundIndex - diffIndex)
      const aroundUserMediation = userMediations[afterAroundIndex]
      const aroundContent = getContentFromUserMediation(aroundUserMediation)
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: aroundContent.id }})
      return
    }
    // update
    if (hasSyncRequested) {
      this.setState({ hasSyncRequested: false })
    }
  }
  handleSetContents = (config = {}) => {
    // unpack and check
    const { dirtyUserMediations } = this
    const { isDebug } = this.props
    const aroundIndex = config.aroundIndex || this.state.aroundIndex
    const userMediations = config.userMediations || this.props.userMediations
    if (!userMediations) {
      return
    }
    const newState = {}
    isDebug && console.log(`DEBUG: UserMediationsDeck - handleSetContents aroundIndex=${aroundIndex}`)
    // if aroundIndex is not yet defined
    // determine what should be the actual aroundIndex
    // ie the index inside de userMediations dexie blob that
    // is the centered card
    if (aroundIndex === null) {
      const isReads = userMediations.map(userMediation =>
        userMediation.dateRead !== null)
      isReads.reverse()
      const reversedFirstReadIndex = isReads.indexOf(true)
      if (reversedFirstReadIndex === -1) {
        newState.aroundIndex = 0
      } else {
        newState.aroundIndex = userMediations.length - 1 - reversedFirstReadIndex + 1
        /*
        const dateReads = userMediations.map(userMediation =>
          userMediation.dateRead && moment(userMediation.dateRead))
            .filter(dateRead => dateRead)
        const lastDateRead = moment.max(dateReads)
        const lastReadIndex = dateReads.indexOf(lastDateRead)
        aroundIndex = lastReadIndex
        */
      }
    } else if (dirtyUserMediations) {
      // if we have already an aroundIndex from a previous user mediations
      // make sure to find the equivalent in the new userMediations
      // by matching ids
      const aroundUserMediation = dirtyUserMediations[aroundIndex]
      if (!aroundUserMediation) {
        console.warn('aroundUserMediation is not defined')
        return
      }
      const aroundId = aroundUserMediation.id
      newState.aroundIndex = userMediations.map(userMediation => userMediation.id)
                                           .indexOf(aroundId)
      isDebug && console.log(`DEBUG: UserMediationsDeck - handleSetContents dirtyUserMediations aroundIndex=${aroundIndex}`)
    } else {
      newState.aroundIndex = aroundIndex
    }
    // set the current index
    Object.assign(newState, {
      currentIndex: newState.aroundIndex,
      contents: userMediations.map(getContentFromUserMediation),
      dirtyUserMediations: null
    })
    // update
    this.setState(newState)
  }
  handleNextItemCard = (diffIndex, deckElement) => {
    // unpack
    const { isDebug,
      transitionTimeout,
      userMediations
    } = this.props
    const { contents } = this.state
    isDebug && console.log('DEBUG: UserMediationsDeck - handleNextItemCard')
    // update around
    const aroundIndex = this.state.aroundIndex - diffIndex
    const currentIndex = aroundIndex
    // set state
    this.setState({ currentIndex, aroundIndex })
    // before or after
    diffIndex > 0
      ? this.handleBeforeContent(diffIndex)
      : this.handleAfterContent(diffIndex)
  }
  handleSetReadCard = card => {
    // unpack
    const { isCheckRead, isDebug, requestData } = this.props
    isDebug && console.log('DEBUG: UserMediationsDeck - handleSetReadCard')
    // update dexie
    const nowDate = moment().toISOString()
    const body = [{
      dateRead: nowDate,
      dateUpdated: nowDate,
      id: card.content.id,
      isFavorite: card.content.isFavorite
    }]
    // request
    isCheckRead && requestData('PUT', 'userMediations',
      { _body: body, body: [], sync: true })
  }
  handleTransitionEnd = () => {
    this.props.isDebug && console.log('DEBUG: UserMediationsDeck - handleTransitionEnd')
    if (this.state.dirtyUserMediations) {
      this.handleSetContents()
    }
    this.setState({ isTransitioning: false })
  }
  handleTransitionStart = () => {
    this.setState({ isTransitioning: true })
  }
  componentWillReceiveProps (nextProps) {
    // check
    const { aroundIndex, isDebug, userMediations } = this.props
    isDebug && console.log('DEBUG: UserMediationsDeck - componentWillReceiveProps')
    // check for different userMediations
    if (nextProps.userMediations !== userMediations) {
      isDebug && console.log('DEBUG: UserMediationsDeck - componentWillReceiveProps diff um')
      this.dirtyUserMediations = userMediations
    }
    // special case where the parent has forced the aroundIndex to be something
    if (nextProps.aroundIndex && !aroundIndex) {
      isDebug && console.log(`DEBUG: UserMediationsDeck - componentWillReceiveProps parent aroundIndex`)
      this.handleSetContents(nextProps)
    }
  }
  componentDidUpdate (prevProps, prevState) {
    // unpack
    const { dirtyUserMediations } = this
    const { handleUserMediationChange,
      isDebug,
      userMediations } = this.props
    const { aroundIndex,
      isTransitioning
    } = this.state
    isDebug && console.log(`DEBUG: UserMediationsDeck - componentDidUpdate`)
    // check
    if (userMediations !== prevProps.userMediations) {
      isDebug && console.log(`DEBUG: UserMediationsDeck - componentDidUpdate diff um`)
      // for the first time we have data
      // we can set peacefully content without
      // having fear of transitions in the deck
      if (!isTransitioning || !dirtyUserMediations) {
        this.handleSetContents()
        return
      }
    }
    // aroundIndex change locally
    if (aroundIndex !== prevState.aroundIndex) {
      const aroundUserMediation = userMediations[aroundIndex]
      isDebug && console.log(`DEBUG: UserMediationsDeck - componentDidUpdate diff aroundIndex`)
      if (prevState.aroundIndex === null) {
        // if it is the first time of setting an aroundIndex
        // we need to check that we are not on the edges
        this.handleBeforeContent(0)
        this.handleAfterContent(0)
      } else {
        // if the aroundIndex has changed we can call
        // a parent method that will do things
        // like updating the url by replacing the userMediationId in the path
        handleUserMediationChange && handleUserMediationChange(aroundUserMediation)
      }
    }
  }
  render () {
    // console.log('RENDER: UserMediationsDeck this.props.userMediations', this.props.userMediations && this.props.userMediations.length,
    //  this.props.userMediations && this.props.userMediations.map(um =>
    //    um && `${um.id} ${um.dateRead}`))
    // console.log('RENDER: UserMediationsDeck this.state.contents', this.state.contents && this.state.contents.length,
    //  this.state.contents && this.state.contents.map(content =>
    //    content && `${content.id} ${content.chosenOffer && content.chosenOffer.id} ${content.dateRead}`))
    // console.log('RENDER: UserMediationsDeck this.state.aroundUserMediation', this.props.userMediations && this.props.userMediations[this.state.aroundIndex] && this.props.userMediations[this.state.aroundIndex].id)
    // console.log('RENDER: UserMediationsDeck this.state.aroundIndex', this.state.aroundIndex)
    // console.log('RENDER: UserMediationsDeck this.state.currentIndex', this.state.currentIndex)
    return [
        <Deck {...this.props}
          {...this.state}
          key={0}
          handleTransitionEnd={this.handleTransitionEnd}
          handleTransitionStart={this.handleTransitionStart}
          handleNextItemCard={this.handleNextItemCard}
          handleSetReadCard={this.handleSetReadCard} />,
          IS_DEV && this.props.userMediations && <UserMediationsDebug key={1}
            {...this.props} {...this.state} />
    ]
  }
}

UserMediationsDeck.defaultProps = { countAfterSync: 5,
  countBeforeSync: 1,
  isCheckRead: false,
  // isDebug: true,
  readTimeout: 2000,
  transitionTimeout: 150
}

export default connect(null,{ requestData })(UserMediationsDeck)
