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


    // from the present to the past
    // meet the first not well defined content
    let futureIndex
    let futureVariable
    if (isBlobModel) {
      futureIndex = contents.length - countBeforeSync
      futureVariable = contents[futureIndex]
    } else {
      futureIndex = 2 * handLength + 2
      futureVariable = futureVariable[aroundIndex + (userMediations.length / 2)]
    }
    // if it is not defined
    // it means we need to do ask the backend
    // to update the dexie blob at the good current around
    console.log('futureIndex', futureIndex, contents)
    console.log('futureVariable', futureVariable)
    if (!futureVariable && !hasSyncRequested) {
      this.setState({ contents:
        isBlobModel
          ? [
              ...contents.slice(0, futureIndex),
              { isLoading: true },
              ...contents.slice(futureIndex + 1)
            ]
          : [
              ...contents.slice(0, -1),
              { isLoading: true }
          ],
        hasSyncRequested: true
      })
      console.log('TRIGGER PUSH PULL')
      // sync('dexie-push-pull', { around: aroundContent.id })
      return
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
    if (!userMediations) {
      return
    }
    // determine automatically what should the actual aroundIndex
    // ie the index inside de userMediations dexie blob that
    // is the centered card
    let aroundContent, aroundIndex
    const dateReads = userMediations.map(userMediation =>
      userMediation.dateRead)
    const firstNotReadIndex = dateReads.indexOf(null)
    if (firstNotReadIndex === -1) {
      const lastReadIndex = dateReads.indexOf(Math.max(...dateReads))
      aroundIndex = lastReadIndex
    } else {
      aroundIndex = firstNotReadIndex
    }
    aroundContent = getContentFromUserMediation(userMediations[aroundIndex])
    // determine the before and after
    let afterContents, beforeContents
    // BLOB MODEL
    if (isBlobModel) {
      beforeContents = [...Array(userMediations.length - 2).keys()]
        .map(index => userMediations[aroundIndex - index - 1])
        .map(getContentFromUserMediation)
      beforeContents.reverse()
      afterContents = [...Array(userMediations.length - 2).keys()]
        .map(index => userMediations[aroundIndex + 1 + index])
        .map(getContentFromUserMediation)
    } else {
      // SLOT MODEL
      beforeContents = [...Array(handLength + 1).keys()]
        .map(index => userMediations[aroundIndex - handLength - 1 + index])
        .map(getContentFromUserMediation)
      afterContents = [...Array(handLength + 1).keys()]
        .map(index => userMediations[aroundIndex + 1 + index])
        .map(getContentFromUserMediation)
    }
    // concat
    const contents = [
      ...beforeContents,
      aroundContent,
      ...afterContents
    ]
    // update
    this.setState({ aroundIndex, contents })
  }
  onNextCard = (diffIndex, deckProps, deckState) => {
    // unpack
    const { handLength,
      isBlobModel,
      nextTimeout,
      userMediations
    } = this.props
    const { aroundIndex, contents } = this.state
    if (isBlobModel) {
      this.handleCheckContent(this.props)
    } else {
      // SLOT MODEL
      setTimeout(() => this.setState({
          aroundIndex: aroundIndex - diffIndex,
          contents: diffIndex === -1
            ? [
              ...contents.slice(1),
              getContentFromUserMediation(userMediations[aroundIndex + handLength + 2])
            ]
            : [
              getContentFromUserMediation(userMediations[aroundIndex - handLength - 2]),
              ...contents.slice(0, -1)
            ]
        }), nextTimeout)
    }
  }
  onReadCard = card => {
    // unpack
    const { requestData } = this.props
    // update dexie
    const nowDate = moment().toISOString()
    const body = [{
      dateRead: nowDate,
      dateUpdated: nowDate,
      id: card.content.id,
      isFavorite: card.content.isFavorite
    }]
    // requestData('PUT', 'userMediations', { body, sync: true })
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
    console.log('RENDER this.state.contents', this.state.contents && this.state.contents.map(content =>
      content && content.id))
    return <Deck {...this.props}
      {...this.state}
      onNextCard={this.onNextCard}
      onReadCard={this.onReadCard} />
  }
}

UserMediationsDeck.defaultProps = { countBeforeSync: 10,
  handLength: 2,
  isBlobModel: false,
  nextTimeout: 500
}

export default compose(
  connect(
    (state, ownProps) => ({ userMediations: state.data.userMediations }),
    { requestData }
  )
)(UserMediationsDeck)
