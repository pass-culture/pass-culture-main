import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Deck from './Deck'
import UserMediationsDebug from './UserMediationsDebug'
import { requestData } from '../reducers/data'
import { IS_DEV } from '../utils/config'
import { getContentFromUserMediation } from '../utils/content'
import { debug } from '../utils/logguers'
import { worker } from '../workers/dexie/register'

class UserMediationsDeck extends Component {
  constructor() {
    super()
    this.state = { aroundIndex: null,
      contents: null,
      extraContents: null,
      isLoadingBefore: false,
      isLoadingAfter: false,
      isTransitioning: false
    }
  }
  handleBeforeContent = diffIndex => {
    // unpack and check
    const { isDebug,
      userMediations
    } = this.props
    const { aroundIndex,
      beforeLimit,
      contents,
      isLoadingBefore
    } = this.state
    if (aroundIndex === null || aroundIndex < 0) {
      return
    }
    isDebug && debug(`UserMediationsDeck - handleAfterContent aroundIndex=${aroundIndex} beforeLimit=${beforeLimit}`)
    // compute
    const isBeforeSync = aroundIndex < beforeLimit
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isBeforeSync && !isLoadingBefore) {
      const extraContents = contents.map((content, index) =>
        index === 0 && { isLoading: true })
      this.setState({ extraContents,
        isLoadingBefore: true })
      const beforeAroundIndex = Math.max(0, aroundIndex - diffIndex)
      const aroundUserMediation = userMediations[beforeAroundIndex]
      const aroundContent = getContentFromUserMediation(aroundUserMediation)
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: aroundContent.id }})
      return
    }
  }
  handleAfterContent = diffIndex => {
    // check unpack
    const { isDebug,
      userMediations
    } = this.props
    const { afterLimit,
      aroundIndex,
      contents,
      isLoadingAfter
    } = this.state
    isDebug && debug(`UserMediationsDeck - handleAfterContent aroundIndex=${aroundIndex}`)
    if (aroundIndex === null || aroundIndex > userMediations.length) {
      return
    }
    isDebug && debug(`UserMediationsDeck - handleAfterContent aroundIndex=${aroundIndex} afterLimit=${afterLimit}`)
    // compute
    const isAfterSync = aroundIndex > afterLimit
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isAfterSync && !isLoadingAfter) {
      const extraContents = contents.map((content, index) =>
        index === contents.length - 1 && { isLoading: true })
      this.setState({ extraContents,
        isLoadingAfter: true })
      const afterAroundIndex = Math.min(userMediations.length - 1,
        aroundIndex - diffIndex)
      const aroundUserMediation = userMediations[afterAroundIndex]
      const aroundContent = getContentFromUserMediation(aroundUserMediation)
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: aroundContent.id }})
      return
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
    isDebug && debug(`UserMediationsDeck - handleSetContents aroundIndex=${aroundIndex}`)
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
    Object.assign(newState, { currentIndex: aroundIndex + 1,
      contents: [{}].concat(userMediations.map(getContentFromUserMediation))
        .concat([{}]),
      dirtyUserMediations: null
    })
    // update
    this.setState(newState)
  }
  handleNextItemCard = (diffIndex, deckElement) => {
    // unpack
    const { isDebug } = this.props
    isDebug && debug('UserMediationsDeck - handleNextItemCard')
    // update around
    const aroundIndex = this.state.aroundIndex - diffIndex
    // set state
    this.setState({ aroundIndex })
    // before or after
    diffIndex > 0
      ? this.handleBeforeContent(diffIndex)
      : this.handleAfterContent(diffIndex)
  }
  handleSetAfterLimit = props => {
    const { afterCount, userMediations } = props
    if (!userMediations) {
      return
    }
    let afterLimit = userMediations.length - 3 - afterCount
    if (afterLimit < 1) { afterLimit = userMediations.length }
    this.setState({ afterLimit })
  }
  handleSetBeforeLimit = props => {
    const { beforeCount, userMediations } = props
    const beforeLimit = Math.min(beforeCount + 1)
    this.setState({ beforeLimit })
  }
  handleSetReadCard = card => {
    // unpack
    const { isCheckRead, isDebug, requestData } = this.props
    isDebug && debug('UserMediationsDeck - handleSetReadCard')
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
    this.props.isDebug && debug('UserMediationsDeck - handleTransitionEnd')
    if (this.state.dirtyUserMediations) {
      this.handleSetContents()
    }
    this.setState({ isTransitioning: false })
  }
  handleTransitionStart = () => {
    this.setState({ isTransitioning: true })
  }
  componentWillMount () {
    this.handleSetContents(this.props)
    this.handleSetAfterLimit(this.props)
    this.handleSetBeforeLimit(this.props)
  }
  componentWillReceiveProps (nextProps) {
    // check
    const { afterCount,
      aroundIndex,
      beforeCount,
      isDebug,
      userMediations
    } = this.props
    isDebug && debug('UserMediationsDeck - componentWillReceiveProps')
    // check for different userMediations
    if (nextProps.userMediations !== userMediations) {
      isDebug && debug('UserMediationsDeck - componentWillReceiveProps diff um')
      this.dirtyUserMediations = userMediations
      this.setState({ isLoadingBefore: false, isLoadingAfter: false })
    } else {
      this.dirtyUserMediations = null
    }
    // special case where the parent has forced the aroundIndex to be something
    if (nextProps.aroundIndex && !aroundIndex) {
      isDebug && debug(`UserMediationsDeck - componentWillReceiveProps parent aroundIndex`)
      this.handleSetContents(nextProps)
    }
    if (nextProps.beforeCount !== beforeCount) {
      this.handleSetBeforeLimit(nextProps)
    }
    if (nextProps.userMediations !== userMediations || nextProps.afterCount !== afterCount) {
      this.handleSetAfterLimit(nextProps)
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
    isDebug && debug(`UserMediationsDeck - componentDidUpdate`)
    // check
    if (userMediations !== prevProps.userMediations) {
      isDebug && debug(`UserMediationsDeck - componentDidUpdate diff um`)
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
      isDebug && debug(`UserMediationsDeck - componentDidUpdate diff aroundIndex`)
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
    // console.log(`RENDER: UserMediationsDeck isLoadingBefore ${this.state.isLoadingBefore} isLoadingAfter ${this.state.isLoadingAfter}`)
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

UserMediationsDeck.defaultProps = { afterCount: 5,
  beforeCount: 2,
  isCheckRead: false,
  // isDebug: true,
  readTimeout: 2000,
  transitionTimeout: 150
}

export default connect(null,{ requestData })(UserMediationsDeck)
