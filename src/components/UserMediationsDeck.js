import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Deck from './Deck'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'
import { closeLoading, showLoading } from '../reducers/loading'
import { getContentFromUserMediation } from '../utils/content'
import { sync } from '../utils/registerDexieServiceWorker'

class UserMediationsDeck extends Component {
  constructor() {
    super()
    this.state = { contents: null, hasSyncRequested: false }
  }
  handleCheckContent = props => {
    // unpack and check
    const { afterContents,
      aroundContent,
      beforeContents
    } = this
    const { requestData, size } = this.props
    const { hasSyncRequested } = this.state
    if (!aroundContent) {
      return
    }
    // from the present to the past
    // meet the first not well defined content
    for (let index of [...Array(size + 1).keys()]) {
      const content = beforeContents[size - 1 - index]
      // if it is not defined
      // it means we need to do ask the backend
      // to update the dexie blob at the good current around
      if (!content && !hasSyncRequested) {
        beforeContents[size - 1 - index] = { isLoading: true }
        this.setState({ contents: [
            ...beforeContents,
            aroundContent,
            ...afterContents
          ],
          hasSyncRequested: true
        })
        sync('dexie-push-pull', { around: aroundContent.id })
        return
      } else if (!hasSyncRequested) {
        this.setState({ hasSyncRequested: false })
      }
    }
    // from the present to the future
    // meet the first not well defined content
    for (let index of [...Array(size + 1).keys()]) {
      const content = afterContents[index]
      // if it is not defined
      // it means we need to do ask the backend
      // to update the dexie blob at the good current around
      if (!content && !hasSyncRequested) {
        afterContents[size - 1 - index] = { isLoading: true }
        this.setState({ contents: [
            ...beforeContents,
            aroundContent,
            ...afterContents
          ],
          hasSyncRequested: true
        })
        sync('dexie-push-pull', { around: aroundContent.id })
        return
      } else if (!hasSyncRequested) {
        this.setState({ hasSyncRequested: false })
      }
    }
  }
  handleSetAroundContent = props => {
    // unpack and check
    const { userMediations } = props
    if (!userMediations) {
      return
    }
    // determine automatically what should the actual aroundIndex
    // ie the index inside de userMediations dexie blob that
    // is the centered card
    const dateReads = userMediations.map(userMediation =>
      userMediation.dateRead)
    const firstNotReadIndex = dateReads.indexOf(null)
    if (firstNotReadIndex === -1) {
      const lastReadIndex = dateReads.indexOf(Math.max(...dateReads))
      this.aroundIndex = lastReadIndex
    } else {
      this.aroundIndex = firstNotReadIndex
    }
    this.aroundContent = getContentFromUserMediation(userMediations[this.aroundIndex])
  }
  handleSetContents = props => {
    // unpack and check
    const { aroundContent } = this
    const { size, userMediations } = props
    if (!aroundContent || !userMediations) {
      return
    }
    // before and after
    this.beforeContents = [...Array(size + 1).keys()]
      .map(index => userMediations[this.aroundIndex - size - 1 + index])
      .map(getContentFromUserMediation)
    this.afterContents = [...Array(size + 1).keys()]
      .map(index => userMediations[this.aroundIndex + 1 + index])
      .map(getContentFromUserMediation)
    // concat
    this.contents = [
      ...this.beforeContents,
      this.aroundContent,
      ...this.afterContents
    ]
    // update
    this.setState({ contents: this.contents })
  }
  onNextCard = diffIndex => {
    /*
    this.aroundIndex = this.aroundIndex - diffIndex
    this.aroundContent = getContentFromUserMediation(userMediations[this.aroundIndex])
    this.handleSetContents(nextProps)
    this.handleCheckContent(nextProps)
    */
    console.log('this.state.contents', this.state.contents.map(content =>
      content && content.id))
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
    this.handleSetAroundContent(this.props)
    this.handleSetContents(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.userMediations !== this.props.userMediations) {
      this.handleSetAroundContent(nextProps)
      this.handleSetContents(nextProps)
      this.handleCheckContent(nextProps)
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

UserMediationsDeck.defaultProps = {
  size: 2
}

export default compose(
  connect(
    (state, ownProps) => ({ userMediations: state.data.userMediations }),
    { requestData }
  )
)(UserMediationsDeck)
