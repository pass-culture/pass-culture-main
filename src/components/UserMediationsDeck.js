import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Deck from './Deck'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'
import { closeLoading, showLoading } from '../reducers/loading'
import { getContentFromUserMediation } from '../utils/content'

class UserMediationsDeck extends Component {
  constructor() {
    super()
    this.around = null
    this.state = { contents: null }
  }
  handleAround = props => {
    const { userMediations } = props
    if (!userMediations || this.around !== null) {
      return
    }
    let around
    const dateReads = userMediations.map(userMediation =>
      userMediation.dateRead)
    const firstNotReadIndex = dateReads.indexOf(null)
    if (firstNotReadIndex === -1) {
      const lastReadIndex = dateReads.indexOf(Math.max(...dateReads))
      around = lastReadIndex
    } else {
      around = firstNotReadIndex
    }
    this.around = around
  }
  handleData = props => {
    // unpack and check
    const { around } = this
    const { size, userMediations } = props
    if (around === null || !userMediations) {
      return
    }
    // before and after
    const beforeUserMediations = [...Array(size + 1).keys()].map(index =>
     userMediations[around - size - 1 + index])
    const currentUserMediation = userMediations[around]
    const afterUserMediations = [...Array(size + 1).keys()].map(index =>
     userMediations[around + 1 + index])
    // concat
    const contents = [
      ...beforeUserMediations,
      currentUserMediation,
      ...afterUserMediations
    ].map(getContentFromUserMediation)
    // update
    this.setState({ contents })
  }
  onNextCard = diffIndex => {
    // this.handleData(this.props)
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
    requestData('PUT', 'userMediations', { body, sync: true })
  }
  componentWillMount () {
    this.handleAround(this.props)
    this.handleData(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.userMediations !== this.props.userMediations) {
      this.handleAround(nextProps)
      this.handleData(nextProps)
    }
  }
  render () {
    /*
    console.log('this.state.contents', this.state.contents.map(content =>
      content && content.id))
    */
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
