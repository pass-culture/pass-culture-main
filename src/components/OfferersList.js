import { requestData } from 'pass-culture-shared'

import React, { Component } from 'react'
import { connect } from 'react-redux'

import OffererItem from './OffererItem'
import offerersSelector from '../selectors/offerers'

class OfferersList extends Component {

  componentDidMount () {
    this.handleDataRequest ()
  }
  componentDidUpdate(prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleDataRequest ()
    }
  }

  handleDataRequest = () => {
    const {
      requestData,
      user
    } = this.props
    user && requestData(
      'GET',
      'offerers',
      {
        normalizer: {
          'managedVenues': 'venues'
        }
      }
    )
  }

  render () {
    const {
      offerers
    } = this.props
    return (
      <ul className="main-list offerers-list">
        {offerers && offerers.map(o =>
          <OffererItem key={o.id} offerer={o} />)}
      </ul>
    )
  }
}

export default connect(
  state => ({
    offerers: offerersSelector(state),
    user: state.user
  }),
  { requestData }
)(OfferersList)
