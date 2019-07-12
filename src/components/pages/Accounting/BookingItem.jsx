import get from 'lodash.get'
import moment from 'moment'
import {
  closeModal,
  Icon,
  showModal,
  showNotification,
  getRequestErrorStringFromErrors,
} from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import selectOfferById from '../../../selectors/selectOfferById'
import selectOffererById from '../../../selectors/selectOffererById'
import selectProductById from '../../../selectors/selectProductById'
import selectStockById from '../../../selectors/selectStockById'
import selectUserById from '../../../selectors/selectUserById'
import selectVenueById from '../../../selectors/selectVenueById'
import { bookingNormalizer } from '../../../utils/normalizers'
import { getOfferTypeLabel } from '../../../utils/offerItem'

const getBookingState = booking => {
  const { isCancelled, isUsed } = booking

  // TODO
  // if (isError) {
  //  return {
  //    picto: 'picto-warning',
  //    message: 'Erreur',
  //    text: '?'
  //  }
  //}

  if (isCancelled === true) {
    return {
      picto: 'picto-warning',
      message: 'Annulé',
    }
  }

  if (isUsed) {
    // TODO
    // if (isPayed) {
    //  return {
    //    picto: 'picto-validation',
    //    message: 'Réglé',
    //  }
    // }

    return {
      picto: 'picto-encours-S',
      message: 'Validé',
    }
  }

  return {
    picto: 'picto-temps-S',
    message: 'En attente',
  }
}

class BookingItem extends Component {
  cancelError = (state, action) => {
    const { dispatch } = this.props
    const {
      payload: { errors },
    } = action

    dispatch(
      showNotification({
        name: 'bookings',
        text: getRequestErrorStringFromErrors(errors),
        type: 'danger',
      })
    )
  }

  handleOnClick = (dispatch, id) => {
    dispatch(
      requestData({
      apiPath: `/bookings/${id}`,
      body: {
        isCancelled: true,
      },
      handleFail: this.cancelError,
      method: 'PATCH',
      normalizer: bookingNormalizer,
      })
    )
    dispatch(closeModal())
  }

  handleOnNoClick = (dispatch) => dispatch(closeModal())

  handleOnCancelClick = () => {
    const { booking, dispatch } = this.props
    const { id } = booking

    dispatch(
      showModal(
        <div>
          {"Souhaitez-vous réellement annuler cette réservation ?"}
          <div className="level">
            <button
              className="button is-primary level-item"
              onClick={this.handleOnClick(dispatch, id)}
              type="button"
            >
              {"Oui"}
            </button>
            <button
              className="button is-primary level-item"
              onClick={this.handleOnNoClick(dispatch)}
              type="button"
            >
              {"Non"}
            </button>
          </div>
        </div>,
        { isUnclosable: true }
      )
    )
  }

  render() {
    const {
      booking,
      offerer,
      stock,
      product,
      venue,
      user,
      offerTypeLabel,
    } = this.props
    const {
      amount,
      dateCreated,
      isCancelled,
      isUsed,
      reimbursed_amount,
      token,
    } = booking
    const { bookingLimitDatetime, groupSize } = stock || {}
    const { email, firstName, lastName } = user || {}
    const userIdentifier =
      firstName && lastName ? `${firstName} ${lastName}` : email
    const { name } = product || {}
    const offererName = get(offerer, 'name')
    const venueName = get(venue, 'name')
    const { picto, message } = getBookingState(booking)

    return (
      <Fragment>
        <tr className="offer-item">
          <td
            className="title"
            colSpan="5"
          >
            {name}
          </td>
          <td
            className="title userName"
            colSpan="5"
          >
            {token}{":"} {userIdentifier}
          </td>
          <td rowSpan="2">
            {!isCancelled && !isUsed && (
              <div className="navbar-item has-dropdown is-hoverable AccountingPage-actions">
                <div className="actionButton" />
                <div className="navbar-dropdown is-right">
                  <a
                    className="navbar-item cancel"
                    onClick={this.handleOnCancelClick}
                  >
                    <Icon svg="ico-close-r" /> Annuler la réservation
                  </a>
                </div>
              </div>
            )}
          </td>
        </tr>
        <tr className="offer-item first-col">
          <td>{moment(dateCreated).format('D/MM/YY')}</td>
          <td>{offerTypeLabel}</td>
          <td>{offererName}</td>
          <td>{venueName}</td>
          <td>
            {groupSize === 1 && <Icon svg="picto-user" />}
            {groupSize > 1 && (
              <Fragment>
                <Icon svg="picto-group" /> {groupSize}
              </Fragment>
            )}
          </td>
          <td>{moment(bookingLimitDatetime).format('D/MM/YY')}</td>
          <td>{"5/10"}</td>
          <td>{amount}</td>
          <td>{reimbursed_amount}</td>
          <td>
            <Icon
              className="picto tiny"
              svg={picto}
            /> {message}
          </td>
        </tr>
      </Fragment>
    )
  }
}

BookingItem.propTypes = {
  booking: PropTypes.shape().isRequired,
}

function mapStateToProps(state, ownProps) {
  const { booking } = ownProps
  const { stockId } = booking
  const stock = selectStockById(state, stockId)
  const offerId = get(stock, 'offerId')
  const offer = selectOfferById(state, offerId)
  const productId = get(offer, 'productId')
  const product = selectProductById(state, productId)
  const venue = selectVenueById(state, get(offer, 'venueId'))
  const offerer = selectOffererById(state, get(venue, 'managingOffererId'))
  const user = selectUserById(state, ownProps.booking.userId)
  const offerTypeLabel = getOfferTypeLabel(product)

  return {
    offer,
    offerTypeLabel,
    offerer,
    product,
    stock,
    venue,
    user,
  }
}

export default connect(mapStateToProps)(BookingItem)
