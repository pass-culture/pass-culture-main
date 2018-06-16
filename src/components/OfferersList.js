import React, { Component } from 'react'
import { connect } from 'react-redux'

import OffererItem from './OffererItem'
import { requestData } from '../reducers/data'
import selectOfferers from '../selectors/offerers'

class OfferersList extends Component {

  componentDidMount () {
    this.handleRequestData ()
  }
  componentDidUpdate(prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleRequestData ()
    }
  }

  handleRequestData = () => {
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
      <ul className="pc-list offerers-list">
        {offerers && offerers.map(o =>
          <OffererItem key={o.id} offerer={o} />)}
      </ul>
    )
  }
}

export default connect(
  state => ({
    offerers: selectOfferers(state),
    user: state.user
  }),
  { requestData }
)(OfferersList)
