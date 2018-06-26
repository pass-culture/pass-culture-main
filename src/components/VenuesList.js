import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import get from 'lodash.get'

import { requestData } from '../reducers/data'
import createVenuesSelector from '../selectors/createVenues'
import VenueItem from './VenueItem'

class VenuesList extends Component {

  componentDidMount() {
    this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleRequestData()
    }
  }

  handleRequestData =() => {
    const {
      match: { params: { offererId } },
      requestData,
      user
    } = this.props
    if (user && offererId !== 'nouveau') {
      requestData(
        'GET',
        `offerers/${offererId}/venues`,
        {
          key: 'venues',
          normalizer: {
            eventOccurences: {
              key: 'eventOccurences',
              normalizer: {
                event: 'occasions'
              }
            },
            // KEY IN THE OBJECY : //KEY IN THE STATE.DATA
            offers: 'offers'
          }
        }
      )
    }
  }

  render() {
    return (
      <ul className='pc-list venues-list'>
        {get(this.props, 'venues', []).map(v =>
          <VenueItem key={v.id} venueId={v.id} />)}
      </ul>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      user: state.user,
      venues: createVenuesSelector()(state, ownProps.match.params.offererId)
    }),
    { requestData }
  )
)(VenuesList)
