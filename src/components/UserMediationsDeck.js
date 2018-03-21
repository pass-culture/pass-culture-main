// import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Deck from './Deck'
import { requestData } from '../reducers/data'
import { getContentFromUserMediation } from '../utils/content'
import { worker } from '../workers/dexie/register'

class UserMediationsDeck extends Component {
  constructor() {
    super()
    this.state = { aroundIndex: null,
      contents: null,
      hasSyncRequested: false,
      isKeepItems: false,
      items: null
    }
  }
  handleBeforeContent = (diffIndex, deckProps, deckState) => {
    // unpack and check
    const { countBeforeSync,
      isBlobModel,
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
    let isBeforeSync
    if (isBlobModel) {
      console.log('BEFORE', 'aroundIndex', aroundIndex, 'limit', countBeforeSync)
      isBeforeSync = aroundIndex < countBeforeSync + 1
    }
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isBeforeSync && !hasSyncRequested) {
      this.setState({ contents: [
          { isLoading: true },
          ...contents.slice(1)
        ],
        hasSyncRequested: true,
        isKeepItems: true
      }, () => this.setState({ isKeepItems: false }))
      // console.log('BEFORE PUSH PULL')
      const aroundUserMediation = userMediations[Math.max(0, aroundIndex)]
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
  handleAfterContent = (diffIndex, deckProps, deckState) => {
    // unpack and check
    const { countAfterSync,
      isBlobModel,
      userMediations
    } = this.props
    const { aroundIndex,
      contents,
      hasSyncRequested
    } = this.state
    if (aroundIndex === null || aroundIndex > userMediations.length) {
      return
    }
    // from the present to the past
    // meet the first not well defined content
    let isAfterSync
    if (isBlobModel) {
      console.log('FUTURE', 'aroundIndex', aroundIndex, 'limit', userMediations.length - 1 - countAfterSync)
      isAfterSync = aroundIndex > userMediations.length - 1 - countAfterSync
    } else {
      isAfterSync = typeof userMediations[
        aroundIndex + (userMediations.length / 2)
      ] === 'undefined'
    }
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isAfterSync && !hasSyncRequested) {
      this.setState({ contents: [
          ...contents.slice(0, -1),
          { isLoading: true }
        ],
        hasSyncRequested: true,
        isKeepItems: true
      }, () => this.setState({ isKeepItems: false }))
      // console.log('AFTER PUSH PULL')
      const aroundUserMediation = userMediations[Math.min(userMediations.length - 1, aroundIndex)]
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
  handleSetContents = (props, prevProps) => {
    // unpack and check
    const { isBlobModel,
      handLength,
      userMediations
    } = props
    let aroundIndex = props.aroundIndex || this.state.aroundIndex
    if (!userMediations) {
      return
    }
    const newState = {}
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
        aroundIndex = 0
      } else {
        aroundIndex = userMediations.length - 1 - reversedFirstReadIndex + 1
        /*
        const dateReads = userMediations.map(userMediation =>
          userMediation.dateRead && moment(userMediation.dateRead))
            .filter(dateRead => dateRead)
        const lastDateRead = moment.max(dateReads)
        const lastReadIndex = dateReads.indexOf(lastDateRead)
        aroundIndex = lastReadIndex
        */
      }
    } else if (prevProps && prevProps.userMediations) {
      // if we have already an aroundIndex from a previous user mediations
      // make sure to find the equivalent in the new userMediations
      // by matching ids
      const aroundUserMediation = prevProps.userMediations[aroundIndex]
      if (!aroundUserMediation) {
        console.warn('aroundUserMediation is not defined')
        return
      }
      const aroundId = aroundUserMediation.id
      aroundIndex = userMediations.map(userMediation => userMediation.id)
                                  .indexOf(aroundId)
    }
    newState.aroundIndex = aroundIndex
    const aroundContent = getContentFromUserMediation(userMediations[aroundIndex])
    // determine the before and after
    const beforeContentsLength = isBlobModel
      // ? userMediations.length - 2
      ? aroundIndex + handLength + 1
      : handLength + 1
    const afterContentsLength = isBlobModel
      // ? userMediations.length - 2
      ? userMediations.length + handLength - aroundIndex
      : handLength + 1
    const beforeContents = [...Array(beforeContentsLength).keys()]
        .map(index => userMediations[isBlobModel
          ? aroundIndex - index - 1
          : aroundIndex - handLength - 1 + index
        ])
        .map(getContentFromUserMediation)
    isBlobModel && beforeContents.reverse()
    const afterContents = [...Array(afterContentsLength).keys()]
        .map(index => userMediations[aroundIndex + 1 + index])
        .map(getContentFromUserMediation)
    // loop for completing the blob if we are closed to the end
    let loopContents = []
    const lastUserMediation = userMediations.slice(-1)[0]
    if (lastUserMediation && lastUserMediation.isLast) {
      if (prevProps && prevProps.userMediations) {
        console.log(lastUserMediation.blobSize, userMediations.length)
        loopContents = prevProps.userMediations.slice(0,
          lastUserMediation.blobSize - prevProps.userMediations.length)
      } else {
        // should request loop data
      }
    }
    // concat
    newState.contents = [
      ...beforeContents,
      aroundContent,
      ...afterContents,
      ...loopContents
    ]
    // update
    this.setState(newState)
  }
  handleNextItemCard = (diffIndex, deckElement) => {
    // unpack
    const { handLength,
      isBlobModel,
      transitionTimeout,
      userMediations
    } = this.props
    const { contents } = this.state
    // update around
    const aroundIndex = this.state.aroundIndex - diffIndex
    // set state
    if (isBlobModel) {
      this.setState({ aroundIndex })
      if (!this.isHandlingContent) {
        diffIndex > 0
          ? this.handleBeforeContent()
          : this.handleAfterContent()
      }
    } else {
      // SLOT MODEL
      setTimeout(() => this.setState({
        contents: diffIndex === -1
          ? [
            ...contents.slice(1),
            getContentFromUserMediation(userMediations[aroundIndex + handLength + 2])
          ]
          : [
            getContentFromUserMediation(userMediations[aroundIndex - handLength - 2]),
            ...contents.slice(0, -1)
          ]
      }), transitionTimeout)
    }
  }
  handleSetReadCard = card => {
    // unpack
    // const {
    //   isCheckRead,
    //   requestData
    // } = this.props
    // update dexie
    // const nowDate = moment().toISOString()
    // const body = [{
    //   dateRead: nowDate,
    //   dateUpdated: nowDate,
    //   id: card.content.id,
    //   isFavorite: card.content.isFavorite
    // }]
    // request
    // console.log('READ CARD', card.index, card.item, card.content.id)
    // isCheckRead && requestData('PUT', 'userMediations', { body, sync: true })
  }
  componentWillMount () {
    // this.handleSetContents(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (
      nextProps.userMediations !== this.props.userMediations ||
      nextProps.aroundIndex !== this.props.aroundIndex
    ) {
      // console.log('')
      // console.log('nextProps.userMediations', nextProps.userMediations && nextProps.userMediations.map(um => um && `${um.id} ${um.dateRead}`))
      // console.log('this.props.userMediations', this.props.userMediations && this.props.userMediations.map(um => um && `${um.id} ${um.dateRead}`))
      // this.handleSetContents(nextProps, this.props)
    }
  }
  componentDidUpdate (prevProps, prevState) {
    const { handleUserMediationChange, userMediations } = this.props
    const { aroundIndex } = this.state
    if (aroundIndex !== prevState.aroundIndex) {
      const aroundUserMediation = userMediations[aroundIndex]
      handleUserMediationChange && handleUserMediationChange(aroundUserMediation)
    }
  }
  render () {
    // console.log('RENDER USERMEDIATIONSDECK this.props.userMediations', this.props.userMediations && this.props.userMediations.length,
    //  this.props.userMediations && this.props.userMediations.map(um =>
    //    um && `${um.id} ${um.dateRead}`))
    //console.log('RENDER USERMEDIATIONSDECK this.state.contents', this.state.contents && this.state.contents.length,
    //  this.state.contents && this.state.contents.map(content =>
    //    content && `${content.id} ${content.dateRead}`))
    return <Deck {...this.props}
      {...this.state}
      handleNextItemCard={this.handleNextItemCard}
      handleSetReadCard={this.handleSetReadCard} />
  }
}

UserMediationsDeck.defaultProps = { countAfterSync: 5,
  countBeforeSync: 1,
  handLength: 2,
  isBlobModel: false,
  isCheckRead: false,
  readTimeout: 2000,
  transitionTimeout: 500
}

export default compose(
  connect(
    (state, ownProps) => ({ userMediations: state.data.userMediations }),
    { requestData }
  )
)(UserMediationsDeck)
