import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Deck from './Deck'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'
import { closeLoading, showLoading } from '../reducers/loading'
import { getCardFromUserMediation } from '../utils/cards'

class UserMediationsDeck extends Component {
  constructor() {
    super()
    this.state = { cards: null }
  }
  handleData = props => {
    const { size, userMediations } = props
    if (!userMediations) {
      return
    }
    let currentIndex
    const dateReads = userMediations.map(userMediation =>
      userMediation.dateRead)
    const firstNotReadIndex = dateReads.indexOf(null)
    if (firstNotReadIndex === -1) {
      const lastReadIndex = dateReads.indexOf(Math.max(...dateReads))
      currentIndex = lastReadIndex
    } else {
      currentIndex = firstNotReadIndex
    }
    console.log('userMediations', userMediations)
    console.log('currentIndex', currentIndex, 'size', size)
    const beforeUserMediations = [...Array(size + 1).keys()].map(index =>
     userMediations[currentIndex - size - 1 + index])
    console.log('beforeUserMediations', beforeUserMediations)
    const currentUserMediation = userMediations[currentIndex]
    const afterUserMediations = [...Array(size + 1).keys()].map(index =>
     userMediations[currentIndex + 1 + index])
    console.log('afterUserMediations', afterUserMediations)
    const contents = [
      ...beforeUserMediations,
      currentUserMediation,
      ...afterUserMediations
    ].map(getCardFromUserMediation)
    this.setState({ currentIndex, contents })
  }
  componentWillMount () {
    this.handleData(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.userMediations !== this.props.userMediations) {
      this.handleData(nextProps)
    }
  }
  render () {
    return <Deck {...this.props} {...this.state} />
  }
}

UserMediationsDeck.defaultProps = {
  size: 2
}

export default compose(
  connect(
    (state, ownProps) => ({ userMediations: state.data.userMediations })
  )
)(UserMediationsDeck)
