import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { List } from 'react-virtualized'
import { withRouter } from 'react-router'

import { requestData } from '../reducers/data'
import selectCurrentOfferer from '../selectors/currentOfferer'
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
    if (this.props.user && this.props.id) {
      this.props.requestData('GET', `offerers/${this.props.id}/venues`, { key: 'venues' })
    }
  }
  render() {
    const {
      managedVenues
    } = this.props
    return (
      <div className="managedVenues-list">

        {
         managedVenues && managedVenues.length
            ? <List
              height={400}
              rowCount={managedVenues.length}
              rowHeight={190}
              rowRenderer={({ index, key, style }) => (
                <div key={index} style={style}>
                  <VenueItem {...managedVenues[index]} />
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
    (state, ownProps) => Object.assign(
      { user: state.user,
       venues: state => state.data.venues },
      selectCurrentOfferer(state, ownProps)
    ),
    { requestData }
  )
)(VenuesList)
