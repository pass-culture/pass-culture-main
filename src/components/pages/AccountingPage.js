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
import offerersSelector from '../../selectors/offerers'
import searchSelector from '../../selectors/search'
import BookingItem from '../items/BookingItem'
import Main from '../layout/Main'

class AccoutingPage extends Component {
  fetchBookings(handleSuccess = () => {}, handleFail = () => {}) {
    this.props.requestData(
      'GET',
      `/offerers/${this.props.offerer.id}/bookings`,
      {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          this.props.goToNextSearchPage()
        },
        key: 'bookings',
        handleFail,
      }
    )
  }

  fetchOfferers(handleSuccess = () => {}, handleFail = () => {}) {
    const { goToNextSearchPage, requestData, offerer } = this.props

    this.props.requestData('GET', '/offerers', {
      handleSuccess: (state, action) => {
        handleSuccess(state, action)
        this.fetchBookings()
      },
      key: 'offerers',
      handlefail: () => {},
    })
  }

  handleOffererFilter() {}

  handleDataRequest(handleSuccess, handleFail) {
    this.fetchOfferers(handleSuccess, handleFail)
  }

  render() {
    const {
      handleOrderByChange,
      handleOrderDirectionChange,
      bookings,
      offerer,
      queryParams,
    } = this.props

    const { order_by } = queryParams || {}
    const [orderBy, orderDirection] = (order_by || '').split('+')

    return (
      <Main
        name="accounting"
        handleDataRequest={this.handleDataRequest.bind(this)}>
        <div className="section">
          <h1 className="main-title">Vos Bookings</h1>
        </div>
        <div className="section">
          <div className="list-header">
            {offerer && (
              <div>
                Filtrer par:
                <span className="select is-rounded is-small">
                  <select
                    onChange={this.handleOffererFilter}
                    className=""
                    value={offerer.id}>
                    <option value={offerer.id}>{offerer.name}</option>
                  </select>
                </span>
              </div>
            )}
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
              handleLoadMore={this.handleDataRequest.bind(this)}>
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
      const offerers = offerersSelector(state)
      let offererId = queryParams.offererId
      if (!offererId && offerers.length > 0) {
        offererId = offerers[0].id
      }

      return {
        bookings: bookingsSelector(state),
        offerer: offererSelector(state, offererId),
        queryParams,
        user: state.user,
      }
    },
    { showModal, requestData, assignData }
  )
)(AccoutingPage)
