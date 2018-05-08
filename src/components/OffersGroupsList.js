import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { AutoSizer, List } from 'react-virtualized'
import { compose } from 'redux'
import { createSelector } from 'reselect'

import OffersGroupItem from './OffersGroupItem'
import { assignData, requestData } from '../reducers/data'
import selectSortedOffersGroups from '../selectors/sortedOffersGroups'

class OffersGroupsList extends Component {
  handleRequestData = () => {
    const {
      match: { params: { offererId } },
      requestData
    } = this.props
    requestData('GET', `offers?offererId=${offererId}`)
  }

  componentWillMount() {
    this.props.user && this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { user } = this.props
    if (user && user !== prevProps.user) {
      this.handleRequestData()
    }
  }

  componentWillUnmount () {
    this.props.assignData({ offers: null })
  }

  render() {
    const { groups } = this.props
    return (
      <div className="offers-groups-list">
        <hr className='is-invisible' key='first'/>
        <AutoSizer>
        {
          ({width, height}) => groups && groups.length ? <List
            height={height}
            rowCount={groups.length}
            rowHeight={190}
            rowRenderer={({ index, key, style }) => (
              <div key={index} style={style}>
                <OffersGroupItem
                  offers={groups[index]}
                  isMediations
                  isModify
                  isPrices
                />
                {
                  (index !== groups.length -1) &&
                  <hr />
                }
              </div>
            )}
            width={width}
          /> : ''
        }
        </AutoSizer>
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({
      groups: selectSortedOffersGroups(state),
      user: state.user,
    }),
    { assignData, requestData }
  )
)(OffersGroupsList)
