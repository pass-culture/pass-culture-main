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
    let pastIndex
    let pastVariable
    if (isBlobModel) {
      pastIndex = countBeforeSync
      pastVariable = contents[pastIndex]
    } else {
      pastIndex = 0
      pastVariable = userMediations[aroundIndex - (userMediations.length / 2)]
    }
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    /*
    if (!pastVariable && !hasSyncRequested) {
      this.setState({ contents:
        isBlobModel
          ? [
              ...contents.slice(0, pastIndex),
              { isLoading: true },
              ...contents.slice(pastIndex + 1)
            ]
          : [
              { isLoading: true },
              ...contents.slice(1)
          ],
        hasSyncRequested: true
      })
      // sync('dexie-push-pull', { around: aroundContent.id })
      return
    } else if (!hasSyncRequested) {
      this.setState({ hasSyncRequested: false })
    }
    */

    // from the present to the past
    // meet the first not well defined content
    let isFutureSync
    if (isBlobModel) {
      // console.log('aroundIndex', aroundIndex, (contents.length / 2) - countBeforeSync)
      isFutureSync = aroundIndex > (contents.length / 2) - countBeforeSync
    } else {
      isFutureSync = typeof userMediations[
        aroundIndex + (userMediations.length / 2)
      ] === 'undefined'
    }
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    // console.log('isFutureSync', isFutureSync, hasSyncRequested)
    if (isFutureSync && !hasSyncRequested) {
      this.setState({ contents: [
          ...contents.slice(0, -1),
          { isLoading: true }
        ],
        hasSyncRequested: true,
        isKeepItems: true
      }, () => this.setState({ isKeepItems: false }))
      // console.log('TRIGGER PUSH PULL')
      const aroundContent = getContentFromUserMediation(userMediations[aroundIndex])
      sync('dexie-push-pull', { around: aroundContent.id })
    } else if (!hasSyncRequested) {
      this.setState({ hasSyncRequested: false })
    }
  }
  handleSetContents = props => {
    // unpack and check
    const { isBlobModel,
      handLength,
      userMediations
    } = props
    let { aroundIndex } = this.state
    if (!userMediations) {
      return
    }
    // if aroundIndex is not yet defined
    // determine what should be the actual aroundIndex
    // ie the index inside de userMediations dexie blob that
    // is the centered card
    if (aroundIndex === null) {
      const dateReads = userMediations.map(userMediation =>
        userMediation.dateRead)
      const firstNotReadIndex = dateReads.indexOf(null)
      if (firstNotReadIndex === -1) {
        const lastReadIndex = dateReads.indexOf(Math.max(...dateReads))
        aroundIndex = lastReadIndex
      } else {
        aroundIndex = firstNotReadIndex
      }
    }
    const aroundContent = getContentFromUserMediation(userMediations[aroundIndex])
    // determine the before and after
    const beforeOrAfterContentsLength = isBlobModel
      ? userMediations.length - 2
      : handLength + 1
    const beforeContents = [...Array(beforeOrAfterContentsLength).keys()]
        .map(index => userMediations[isBlobModel
          ? aroundIndex - index - 1
          : aroundIndex - handLength - 1 + index
        ])
        .map(getContentFromUserMediation)
      isBlobModel && beforeContents.reverse()
    const afterContents = [...Array(beforeOrAfterContentsLength).keys()]
        .map(index => userMediations[aroundIndex + 1 + index])
        .map(getContentFromUserMediation)
    // concat
    const contents = [
      ...beforeContents,
      aroundContent,
      ...afterContents
    ]
    // update
    this.setState({ aroundIndex,
      contents
    })
  }
  onNextCard = (diffIndex, deckProps, deckState) => {
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
        aroundIndex,
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
  onReadCard = card => {
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
      this.handleSetContents(nextProps)
      // this.handleCheckContent(nextProps)
    }
  }
  render () {
    //console.log('RENDER this.state.contents', this.state.contents && this.state.contents.map(content =>
    //  content && content.id))
    return <Deck {...this.props}
      {...this.state}
      onNextCard={this.onNextCard}
      onReadCard={this.onReadCard} />
  }
}

UserMediationsDeck.defaultProps = { countBeforeSync: 10,
  handLength: 2,
  isBlobModel: false,
  isCheckRead: true,
  readTimeout: 2000,
  transitionTimeout: 500
}

export default compose(
  connect(
    (state, ownProps) => ({ userMediations: state.data.userMediations }),
    { requestData }
  )
)(UserMediationsDeck)
