import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Deck from './Deck'
import { requestData } from '../reducers/data'
import { getContentFromUserMediation } from '../utils/content'
import { sync } from '../utils/registerDexieServiceWorker'

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
  handleCheckContent = props => {
    // unpack and check
    const { countBeforeSync,
      isBlobModel,
      requestData,
      handLength,
      userMediations
    } = props
    const { aroundIndex,
      contents,
      hasSyncRequested
    } = this.state
    if (aroundIndex === null) {
      return
    }
    // from the present to the past
    // meet the first not well defined content
    let isPastSync
    if (isBlobModel) {
      console.log('PAST', 'aroundIndex', aroundIndex, 'limit', countBeforeSync)
      isPastSync = aroundIndex < countBeforeSync
    }
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isPastSync && !hasSyncRequested) {
      this.setState({ contents: [
          { isLoading: true },
          ...contents.slice(1)
        ],
        hasSyncRequested: true,
        isKeepItems: true
      }, () => this.setState({ isKeepItems: false }))
      console.log('TRIGGER PUSH PULL')
      const aroundContent = getContentFromUserMediation(userMediations[aroundIndex])
      sync('dexie-push-pull', { around: aroundContent.id })
      return
    }
    // from the present to the past
    // meet the first not well defined content
    let isFutureSync
    if (isBlobModel) {
      console.log('FUTURE', 'aroundIndex', aroundIndex, 'limit', userMediations.length - 1 - countBeforeSync)
      isFutureSync = aroundIndex > userMediations.length - 1 - countBeforeSync
    } else {
      isFutureSync = typeof userMediations[
        aroundIndex + (userMediations.length / 2)
      ] === 'undefined'
    }
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    if (isFutureSync && !hasSyncRequested) {
      this.setState({ contents: [
          ...contents.slice(0, -1),
          { isLoading: true }
        ],
        hasSyncRequested: true,
        isKeepItems: true
      }, () => this.setState({ isKeepItems: false }))
      console.log('TRIGGER PUSH PULL')
      const aroundContent = getContentFromUserMediation(userMediations[aroundIndex])
      sync('dexie-push-pull', { around: aroundContent.id })
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
    let { aroundIndex } = this.state
    if (!userMediations) {
      return
    }
    const newState = {}
    // if aroundIndex is not yet defined
    // determine what should be the actual aroundIndex
    // ie the index inside de userMediations dexie blob that
    // is the centered card
    if (prevProps === null || aroundIndex === null) {
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
    } else {
      // if we have already an aroundIndex
      // make sure to find the equivalent in the new userMediations
      // by matching ids
      console.log('REFIND', aroundIndex, prevProps.userMediations[aroundIndex])
      const aroundId = prevProps.userMediations[aroundIndex].id
      aroundIndex = userMediations.map(userMediation => userMediation.id)
                                  .indexOf(aroundId)
      console.log('NEW aroundIndex', aroundIndex)
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
    // concat
    newState.contents = [
      ...beforeContents,
      aroundContent,
      ...afterContents
    ]
    // update
    this.setState(newState)
  }
  handleNextItemCard = (diffIndex, deckProps, deckState) => {
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
      this.handleCheckContent(this.props)
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
    const { isCheckRead, requestData } = this.props
    // update dexie
    const nowDate = moment().toISOString()
    const body = [{
      dateRead: nowDate,
      dateUpdated: nowDate,
      id: card.content.id,
      isFavorite: card.content.isFavorite
    }]
    // request
    // console.log('READ CARD', card.index, card.item, card.content.id)
    isCheckRead && requestData('PUT', 'userMediations', { body, sync: true })
  }
  componentWillMount () {
    this.handleSetContents(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.userMediations !== this.props.userMediations) {
      // console.log('')
      // console.log('nextProps.userMediations', nextProps.userMediations && nextProps.userMediations.map(um => um && `${um.id} ${um.dateRead}`))
      // console.log('this.props.userMediations', this.props.userMediations && this.props.userMediations.map(um => um && `${um.id} ${um.dateRead}`))
      this.handleSetContents(nextProps, this.props)
    }
  }
  render () {
    console.log('RENDER USERMEDIATIONSDECK this.props.userMediations', this.props.userMediations && this.props.userMediations.length,
      this.props.userMediations && this.props.userMediations.map(um =>
        um && `${um.id} ${um.dateRead}`))
    //console.log('RENDER USERMEDIATIONSDECK this.state.contents', this.state.contents && this.state.contents.length,
    //  this.state.contents && this.state.contents.map(content =>
    //    content && `${content.id} ${content.dateRead}`))
    return <Deck {...this.props}
      {...this.state}
      handleNextItemCard={this.handleNextItemCard}
      handleSetReadCard={this.handleSetReadCard} />
  }
}

UserMediationsDeck.defaultProps = { countBeforeSync: 5,
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
