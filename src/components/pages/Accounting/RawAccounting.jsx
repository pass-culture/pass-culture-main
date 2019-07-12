import get from 'lodash.get'
import {
  Icon,
  InfiniteScroller,
  requestData,
  Spinner,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import PropTypes from 'prop-types'

import BookingItem from './BookingItem'
import HeroSection from '../../layout/HeroSection/HeroSection'
import Main from '../../layout/Main'
import { bookingNormalizer, offererNormalizer } from '../../../utils/normalizers'
import { mapApiToWindow } from '../../../utils/pagination'

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
  action: PropTypes.func.isRequired,
  field: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  sort: PropTypes.shape().isRequired,
  style: PropTypes.shape().isRequired,
}

class RawAccouting extends Component {
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

  handleOnSubmit = event => {
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

  handleOnChange = (event, pagination) => () =>
    pagination.change({
      [mapApiToWindow.offererId]: event.target.value,
    })

  onSortChange = (field, currentSort) => {
    let dir = currentSort.dir || 'asc'
    if (currentSort.field === field) {
      dir = dir === 'asc' ? 'desc' : 'asc'
    }

    const { pagination } = this.props
    pagination.change({ orderBy: [field, dir].join('+') })
  }

  render() {
    const { bookings, offerer, offerers, pagination } = this.props
    const { windowQuery } = pagination

    const { orderBy } = windowQuery || {}
    const [orderName, orderDirection] = (orderBy || '').split('+')

    // Inject sort and action once for all
    const Th = ({ field, label, style }) => (
      <TableSortableTh
        action={this.onSortChange}
        field={field}
        label={label}
        sort={{ field: orderName, dir: orderDirection }}
        style={style}
      />
    )

    return (
      <Main
        backTo={{ path: '/accueil', label: 'Accueil' }}
        handleDataRequest={this.handleDataRequest}
        name="accounting"
      >
        <HeroSection
          subtitle="Suivez vos réservations et vos remboursements."
          title="Comptabilité"
        >
          <form
            className="section"
            onSubmit={this.handleOnSubmit}
          />
          <div className="section">
            <div className="list-header">
              {offerer && (
                <div>
                  {"Structure:"}
                  <span className="select is-rounded is-small">
                    <select
                      className=""
                      onChange={this.handleOnChange(event, pagination)}
                      value={offerer.id}
                    >
                      {offerers.map(item => (
                        <option
                          key={item.id}
                          value={item.id}
                        >
                          {item.name}
                        </option>
                      ))}
                    </select>
                  </span>
                </div>
              )}
            </div>

            <table
              className="accounting"
              style={{ width: '100%' }}
            >
              <thead>
                <tr>
                  <th
                    className="first-row"
                    colSpan="5"
                  >
                    {"OFFRE"}
                  </th>
                  <th
                    className="first-row"
                    colSpan="2"
                  >
                    {"RESERVATION"}
                  </th>
                  <th
                    className="first-row"
                    colSpan="4"
                  >
                    {"REMBOURSEMENT"}
                  </th>
                </tr>
                <tr>
                  {/* @TODO: Fix fake key attributes !*/}
                  <Th
                    field="booking.%22dataModified%22"
                    label="Date"
                  />
                  <Th
                    field="category"
                    label="Catégorie"
                  />
                  <Th
                    field="structure"
                    label="Structure"
                  />
                  <Th
                    field="place"
                    label="Lieu"
                  />
                  <Th
                    field="type"
                    label="Type"
                    style={{ width: '60px' }}
                  />
                  <Th
                    field="cancelDate"
                    label="Date limite d'annulation"
                    style={{ width: '100px' }}
                  />
                  <Th
                    field="rate"
                    label="Taux écoulé"
                    style={{ width: '85px' }}
                  />
                  <Th
                    field="passPrice"
                    label="Prix pass"
                    style={{ width: '60px' }}
                  />
                  <Th
                    field="ammount"
                    label="Montant rbt."
                    style={{ width: '80px' }}
                  />
                  <Th
                    field="state"
                    label="État du paiement"
                    style={{ width: '120px' }}
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
                )}
              >
                {bookings.map(booking => (
                  <BookingItem
                    booking={booking}
                    key={booking.id}
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

RawAccouting.propTypes = {
  dispatch: PropTypes.func.isRequired,
}

export default RawAccouting
