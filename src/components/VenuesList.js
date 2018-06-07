import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { List } from 'react-virtualized'
import { withRouter } from 'react-router'

import { requestData } from '../reducers/data'
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
    if (user) {
      requestData(
        'GET',
        `offerers/${offererId}/venues`,
        {
          key: 'venues',
          isMergingArray: false
        }
      )
    }
  }

  render() {
    const { venues } = this.props
    console.log('venues', venues)
    return (
      <div className="venues-list">
        {
         venues && venues.length
            ? <List
              height={400}
              rowCount={venues.length}
              rowHeight={190}
              rowRenderer={({ index, key, style }) => (
                <div key={index} style={style}>
                  <VenueItem {...venues[index]} />
                </div>
              )}
              width={400}
            />
            : "Vous n'avez pas encore ajouté de lieux"
        }
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      user: state.user,
      venues: state.data.venues
    }),
    { requestData }
  )
)(VenuesList)
