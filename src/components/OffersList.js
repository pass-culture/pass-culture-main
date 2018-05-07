import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { List } from 'react-virtualized'
import { compose } from 'redux'
import { createSelector } from 'reselect'

import OfferItem from './OfferItem'
import { requestData } from '../reducers/data'
import selectSortedOffers from '../selectors/sortedOffers'

class OffersList extends Component {
  handleRequestData = props => {
    const {
      match: {
        params: { offererId },
      },
      requestData,
      user,
    } = props
    if (!this.hasRequired && user) {
      requestData('GET', `offers?offererId=${offererId}`)
      this.hasRequired = true
    }
  }

  componentWillMount() {
    this.props.user && this.handleRequestData(this.props)
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.user && nextProps.user !== this.props.user) {
      this.handleRequestData(nextProps)
    }
  }

  render() {
    const { offers } = this.props
    console.log('offers', offers)
    return (
      <div className="offers-list container">
        <hr className='is-invisible' key='first'/>
        {
          offers && <List
            width={1200}
            height={1500}
            rowCount={offers.length}
            rowHeight={100}
            rowRenderer={({ index, key, style }) => (
              <div key={index} style={style}>
                <OfferItem {...offers[index]}
                  isMediations
                  isModify
                  isPrices
                />
                {
                  (index !== offers.length -1) &&
                  <hr />
                }
              </div>
            )}
          />
        }
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({
      offers: selectSortedOffers(state),
      user: state.user,
    }),
    { requestData }
  )
)(OffersList)
