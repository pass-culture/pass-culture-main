import get from 'lodash.get'
import {
  Icon,
  InfiniteScroller,
  requestData,
  Spinner,
  withLogin,
  withSearch,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import bookingsSelector from '../../selectors/bookings'
import HeroSection from '../layout/HeroSection'
import offererSelector from '../../selectors/offerer'
import offerersSelector from '../../selectors/offerers'
import searchSelector from '../../selectors/search'
import { bookingNormalizer, offererNormalizer } from '../../utils/normalizers'
import BookingItem from '../items/BookingItem'
import Main from '../layout/Main'

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

class AccoutingPage extends Component {
  fetchBookings(handleSuccess = () => {}, handleFail = () => {}) {
    const { dispatch, goToNextSearchPage, offerer } = this.props
    offerer &&
      dispatch(
        requestData('GET', `offerers/${get(offerer, 'id')}/bookings`, {
          handleSuccess: (state, action) => {
            handleSuccess(state, action)
            goToNextSearchPage()
          },
          key: 'bookings',
          handleFail,
          normalizer: bookingNormalizer,
          isMergingArray: false,
        })
      )
  }

  fetchOfferers(handleSuccess = () => {}, handleFail = () => {}) {
    this.props.dispatch(
      requestData('GET', 'offerers', {
        handleSuccess: (state, action) => {
          handleSuccess(state, action)
          this.fetchBookings()
        },
        handleFail,
        normalizer: offererNormalizer,
      })
    )
  }

  handleOffererFilter() {}

  handleDataRequest = (handleSuccess, handleFail) => {
    this.fetchOfferers(handleSuccess, handleFail)
  }

  handleSortChange(field, currentSort) {
    let dir = currentSort.dir || 'asc'
    if (currentSort.field === field) {
      dir = dir === 'asc' ? 'desc' : 'asc'
    }

    this.props.handleQueryParamsChange({ order_by: [field, dir].join('+') })
  }

  componentDidUpdate(prevProps) {
    const { handleQueryParamsChange, queryParams, offerers } = this.props
    const offererId = get(queryParams, 'offererId')
    if (
      !offererId &&
      offerers !== prevProps.offerers &&
      get(offerers, 'length')
    ) {
      handleQueryParamsChange({ offererId: offerers[0].id })
    }
  }

  cancelBooking(id) {
    console.log('cancel booking for id:', id)
    this.props.dispatch(
      requestData('DELETE', `/bookings/${id}`, {
        handleSuccess: (state, request) => {
          console.log(request)
        },
        handleFail: (state, request) => {
          console.log(request)
        },
      })
    )
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

    const { order_by } = queryParams || {}
    const [orderBy, orderDirection] = (order_by || '').split('+')

    // Inject sort and action once for all
    const Th = ({ field, label, style }) => (
      <TableSortableTh
        field={field}
        label={label}
        sort={{ field: orderBy, dir: orderDirection }}
        action={this.handleSortChange.bind(this)}
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
        <form className="section" onSubmit={handleSearchChange} />
        <div className="section">
          <div className="list-header">
            {offerer && (
              <div>
                Structure:
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
                <Th label="Date" field="date" />
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
              handleLoadMore={this.handleDataRequest}
              renderLoading={() => (
                <tr>
                  <Spinner Tag="td" style={{ justifyContent: 'center' }} />
                </tr>
              )}>
              {bookings.map(booking => (
                <BookingItem
                  key={booking.id}
                  booking={booking}
                  cancelAction={this.cancelBooking.bind(this)}
                />
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
  const queryParams = searchSelector(state, ownProps.location.search)
  const offerers = offerersSelector(state)
  return {
    bookings: bookingsSelector(state),
    offerer: offererSelector(state, get(queryParams, 'offererId')),
    offerers,
    queryParams,
    user: state.user,
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
  connect(mapStateToProps)
)(AccoutingPage)
