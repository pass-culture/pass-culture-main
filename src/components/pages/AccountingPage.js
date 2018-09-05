import {
  Icon,
  InfiniteScroller,
  requestData,
  withLogin,
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
import { BookingNormalizer } from '../../utils/normalizers'
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
        normalizer: BookingNormalizer,
        isMergingArray: false,
      }
    )
  }

  fetchOfferers(handleSuccess = () => {}, handleFail = () => {}) {
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
      handleSearchChange,
      handleQueryParamsChange,
      bookings,
      offerer,
      offerers,
      queryParams,
    } = this.props

    const { search, order_by } = queryParams || {}
    const [orderBy, orderDirection] = (order_by || '').split('+')

    return (
      <Main
        name="accounting"
        handleDataRequest={this.handleDataRequest.bind(this)}>
        <div className="section">
          <h1 className="main-title">Comptabilité</h1>
        </div>
        <form className="section" onSubmit={handleSearchChange} />
        <div className="section">
          <div className="list-header">
            {offerer && (
              <div>
                Filtrer par:
                <span className="select is-rounded is-small">
                  <select
                    onChange={event =>
                      handleQueryParamsChange({ offererId: event.target.value })
                    }
                    className=""
                    value={offerer.id}>
                    {offerers.map(item => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
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
          <table className="accounting" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th className="first-row" colSpan="5">
                  OFFRE
                </th>
                <th className="first-row" colSpan="2">
                  RESERVATION
                </th>
                <th className="first-row" colSpan="4">
                  REMBOURSEMENT
                </th>
              </tr>
              <tr>
                <th>Date</th>
                <th>Catégorie</th>
                <th>Structure</th>
                <th>Lieu</th>
                <th style={{ width: '50px' }}>Type</th>
                <th style={{ width: '90px' }}>Date limite d'annulation</th>
                <th style={{ width: '50px' }}>Taux écoulé</th>
                <th style={{ width: '40px' }}>Prix pass</th>
                <th style={{ width: '40px' }}>Montant rbt.</th>
                <th style={{ width: '100px' }}>État du paiement</th>
                <th style={{ width: '25px' }} />
              </tr>
            </thead>
            <InfiniteScroller
              Tag="tbody"
              className="offers-list main-list"
              handleLoadMore={this.handleDataRequest.bind(this)}>
              {bookings.map(booking => (
                <BookingItem key={booking.id} booking={booking} />
              ))}
            </InfiniteScroller>
          </table>
        </div>
      </Main>
    )
  }
}

const mapStateToProps = (state, ownProps) => {
  const queryParams = searchSelector(state, ownProps.location.search)
  const offerers = offerersSelector(state)
  let offererId = queryParams.offererId
  if (!offererId && offerers.length > 0) {
    offererId = offerers[0].id
  }

  return {
    bookings: bookingsSelector(state),
    offerer: offererSelector(state, offererId),
    offerers,
    queryParams,
    user: state.user,
  }
}

const mapDispatchToProps = { requestData }

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
    mapStateToProps,
    mapDispatchToProps
  )
)(AccoutingPage)
