import get from 'lodash.get'
import {
  Icon,
  InfiniteScroller,
  requestData,
  Spinner,
  withLogin,
  withPagination,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import BookingItem from './BookingItem'
import HeroSection from '../../layout/HeroSection'
import Main from '../../layout/Main'
import bookingsSelector from '../../../selectors/bookings'
import offererSelector from '../../../selectors/offerer'
import offerersSelector from '../../../selectors/offerers'
import {
  bookingNormalizer,
  offererNormalizer,
} from '../../../utils/normalizers'
import { mapApiToWindow, windowToApiQuery } from '../../../utils/pagination'

const TableSortableTh = ({ field, label, sort, action, style }) => (
  <th style={style}>
    <a onClick={() => action(field, sort)}>
      <span>{label}</span>

      <span className="sortPlaceHolder">
        {sort.field === field && (
          // @TODO: onclick sort action
          <Icon svg={`ico-sort-${sort.dir}ending`} />
        )}
      </span>
    </a>
  </th>
)

TableSortableTh.propTypes = {
  sort: PropTypes.object.isRequired,
  field: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  action: PropTypes.func.isRequired,
  style: PropTypes.object,
}

class Accouting extends Component {
  onSubmit = event => {
    const { pagination } = this.props

    event.preventDefault()

    const value = event.target.elements.search.value

    pagination.change({
      [mapApiToWindow.keywords]: value === '' ? null : value,
    })
  }

  fetchBookings = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { dispatch, pagination, offerer, search } = this.props
    const { apiQueryString, goToNextPage, page } = pagination

    if (!offerer) {
      return
    }

    // BECAUSE THE INFINITE SCROLLER CALLS ONCE THIS FUNCTION
    // BUT THEN PUSH THE SEARCH TO PAGE + 1
    // WE PASS AGAIN HERE FOR THE SAME PAGE
    // SO WE NEED TO PREVENT A SECOND CALL
    // (can be ameliorated late)
    if (page !== 1 && search.page && page === Number(search.page)) {
      return
    }

    const apiPath = `/offerers/${get(offerer, 'id')}/bookings?${apiQueryString}`

    dispatch(
      requestData({
        apiPath,
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          goToNextPage()
        },
        handleFail,
        normalizer: bookingNormalizer,
        stateKey: 'bookings',
      })
    )
  }

  fetchOfferers = (handleSuccess = () => {}, handleFail = () => {}) => {
    const { dispatch } = this.props
    dispatch(
      requestData({
        apiPath: '/offerers',
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          this.fetchBookings()
        },
        handleFail,
        normalizer: offererNormalizer,
      })
    )
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    this.fetchOfferers(handleSuccess, handleFail)
  }

  handleLoadMore = (handleSuccess, handleFail) => {
    this.handleDataRequest(handleSuccess, handleFail)
    const { history, location, pagination } = this.props
    const { windowQueryString, page } = pagination

    const to = `${location.pathname}?page=${page}&${windowQueryString}`

    history.push(to)
  }

  handleSortChange = (field, currentSort) => {
    let dir = currentSort.dir || 'asc'
    if (currentSort.field === field) {
      dir = dir === 'asc' ? 'desc' : 'asc'
    }

    this.props.pagination.change({ orderBy: [field, dir].join('+') })
  }

  componentDidUpdate(prevProps) {
    const { offerers, pagination } = this.props
    const offererId = get(pagination.windowQuery, mapApiToWindow.offererId)
    if (
      !offererId &&
      offerers !== prevProps.offerers &&
      get(offerers, 'length')
    ) {
      pagination.change({ [mapApiToWindow.offererId]: offerers[0].id })
    }
  }

  render() {
    const { bookings, offerer, offerers, pagination } = this.props
    const { windowQuery } = pagination

    const { orderBy } = windowQuery || {}
    const [orderName, orderDirection] = (orderBy || '').split('+')

    // Inject sort and action once for all
    const Th = ({ field, label, style }) => (
      <TableSortableTh
        field={field}
        label={label}
        sort={{ field: orderName, dir: orderDirection }}
        action={this.handleSortChange}
        style={style}
      />
    )

    return (
      <Main
        name="accounting"
        handleDataRequest={this.handleDataRequest}
        backTo={{ path: '/accueil', label: 'Accueil' }}>
        <HeroSection
          subtitle="Suivez vos réservations et vos remboursements."
          title="Comptabilité">
          <form className="section" onSubmit={this.onSubmit} />
          <div className="section">
            <div className="list-header">
              {offerer && (
                <div>
                  Structure:
                  <span className="select is-rounded is-small">
                    <select
                      onChange={event =>
                        pagination.change({
                          [mapApiToWindow.offererId]: event.target.value,
                        })
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
                  {/* @TODO: Fix fake key attributes !*/}
                  <Th label="Date" field="booking.%22dataModified%22" />
                  <Th label="Catégorie" field="category" />
                  <Th label="Structure" field="structure" />
                  <Th label="Lieu" field="place" />
                  <Th style={{ width: '60px' }} label="Type" field="type" />
                  <Th
                    style={{ width: '100px' }}
                    label="Date limite d'annulation"
                    field="cancelDate"
                  />
                  <Th
                    style={{ width: '85px' }}
                    label="Taux écoulé"
                    field="rate"
                  />
                  <Th
                    style={{ width: '60px' }}
                    label="Prix pass"
                    field="passPrice"
                  />
                  <Th
                    style={{ width: '80px' }}
                    label="Montant rbt."
                    field="ammount"
                  />
                  <Th
                    style={{ width: '120px' }}
                    label="État du paiement"
                    field="state"
                  />
                  <th style={{ width: '25px' }} />
                </tr>
              </thead>
              <InfiniteScroller
                Tag="tbody"
                className="offers-list main-list"
                handleLoadMore={this.handleLoadMore}
                renderLoading={() => (
                  <tr>
                    <Spinner
                      Tag="td"
                      colSpan="6"
                      style={{ justifyContent: 'center' }}
                    />
                  </tr>
                )}>
                {bookings.map(booking => (
                  <BookingItem key={booking.id} booking={booking} />
                ))}
              </InfiniteScroller>
            </table>
          </div>
        </HeroSection>
      </Main>
    )
  }
}

const mapStateToProps = (state, ownProps) => {
  const offererId = get(
    ownProps,
    `pagination.windowQuery.${mapApiToWindow.offererId}`
  )

  return {
    bookings: bookingsSelector(state),
    offerer: offererSelector(state, offererId),
    offerers: offerersSelector(state),
    user: state.user,
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  withPagination({
    dataKey: 'bookings',
    defaultWindowQuery: {
      [mapApiToWindow.keywords]: null,
      [mapApiToWindow.offererId]: null,
      [mapApiToWindow.venueId]: null,
      orderBy: 'booking.id+desc',
    },
    windowToApiQuery,
  }),
  connect(mapStateToProps)
)(Accouting)
