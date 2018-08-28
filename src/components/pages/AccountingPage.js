import {
  assignData,
  Icon,
  InfiniteScroller,
  requestData,
  withLogin,
  showModal,
  withSearch,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import bookingsSelector from '../../selectors/bookings'
import offererSelector from '../../selectors/offerer'
import searchSelector from '../../selectors/search'
import BookingItem from '../items/BookingItem'
import Main from '../layout/Main'

class AccoutingPage extends Component {
  handleDataRequest = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { goToNextSearchPage, requestData, types } = this.props
    // @TODO Fix hard coded ID `FU`
    requestData('GET', `/offerers/FU/bookings`, {
      handleSuccess: (state, action) => {
        handleSuccess(state, action)
        goToNextSearchPage()
      },
      key: 'bookings',
      handleFail,
    })
    types.length === 0 && requestData('GET', 'types')
  }

  render() {
    const {
      handleOrderByChange,
      handleOrderDirectionChange,
      bookings,
      queryParams,
    } = this.props

    const { order_by } = queryParams || {}
    const [orderBy, orderDirection] = (order_by || '').split('+')

    return (
      <Main name="accouting" handleDataRequest={this.handleDataRequest}>
        <div className="section">
          <h1 className="main-title">Vos Bookings</h1>
        </div>
        <div className="section">
          <div className="list-header">
            <div>
              <div className="recently-added" />
              Ajouté récemment
            </div>
            <div>
              Trier par:
              <span className="select is-rounded is-small">
                <select
                  onChange={handleOrderByChange}
                  className=""
                  value={orderBy}>
                  <option value="sold">Offres écoulées</option>
                  <option value="createdAt">Date de création</option>
                </select>
              </span>
            </div>
            <div>
              <button
                onClick={handleOrderDirectionChange}
                className="button is-secondary">
                <Icon
                  svg={
                    orderDirection === 'asc'
                      ? 'ico-sort-ascending'
                      : 'ico-sort-descending'
                  }
                />
              </button>
            </div>
          </div>
          {
            <InfiniteScroller
              className="offers-list main-list"
              handleLoadMore={this.handleDataRequest}>
              {bookings.map(booking => (
                <BookingItem key={booking.id} booking={booking} />
              ))}
            </InfiniteScroller>
          }
        </div>
      </Main>
    )
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  withSearch({
    dataKey: 'booking',
    defaultQueryParams: {
      search: undefined,
      order_by: `createdAt+desc`,
      offererId: null,
    },
  }),
  connect(
    (state, ownProps) => {
      const queryParams = searchSelector(state, ownProps.location.search)
      return {
        bookings: bookingsSelector(state, queryParams.offererId),
        offerer: offererSelector(state, queryParams.offererId),
        queryParams,
        user: state.user,
        types: state.data.types,
      }
    },
    { showModal, requestData, assignData }
  )
)(AccoutingPage)
