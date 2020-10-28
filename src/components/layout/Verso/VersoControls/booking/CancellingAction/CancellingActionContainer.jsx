import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { closeSharePopin, openSharePopin } from '../../../../../../redux/actions/share'
import {
  selectBookingByRouterMatch,
  selectPastEventBookingByOfferId,
} from '../../../../../../redux/selectors/data/bookingsSelectors'
import { selectOfferByRouterMatch } from '../../../../../../redux/selectors/data/offersSelectors'
import { selectStockById } from '../../../../../../redux/selectors/data/stocksSelectors'
import { requestData } from '../../../../../../utils/fetch-normalize-data/requestData'
import { bookingNormalizer } from '../../../../../../utils/normalizers'
import withTracking from '../../../../../hocs/withTracking'
import CancellingAction from './CancellingAction'
import PopinButton from './PopinButton'

export const getCancellingUrl = (bookingId, params, pathname, search) => {
  let bookingUrl = pathname

  bookingUrl = `${bookingUrl}/reservation`

  if (params.bookingId === undefined) {
    bookingUrl = `${bookingUrl}/${bookingId}`
  }

  return `${bookingUrl}/annulation${search}`
}

export const mapStateToProps = (state, ownProps) => {
  const { location, match } = ownProps
  const { pathname, search } = location
  const booking = selectBookingByRouterMatch(state, match)
  const cancellingUrl = getCancellingUrl(booking.id, match.params, pathname, search)
  const offer = selectOfferByRouterMatch(state, match)
  const stock = selectStockById(state, booking.stockId)
  const price = stock.price * booking.quantity

  const userPastBookingForThisOffer = selectPastEventBookingByOfferId(state, offer.id)
  const offerCanBeCancelled = userPastBookingForThisOffer === null

  return { booking, cancellingUrl, offer, offerCanBeCancelled, price }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { history, location } = ownProps
  const { pathname, search } = location

  function handleClosePopinAction() {
    dispatch(closeSharePopin())
    const nextPathname = pathname.split(/\/reservation(\/|$|\/$)/)[0]
    const nextUrl = `${nextPathname}${search}`
    history.push(nextUrl)
  }

  const handleOpenFailurePopin = (state, request) => {
    const { payload } = request
    const { errors } = payload
    const { booking: bookingError } = errors || {}
    const message = bookingError || ['Une erreur inconnue s’est produite']
    const options = {
      text: message.join('\n'),
      title: 'Annulation impossible',
    }
    dispatch(openSharePopin(options))
  }

  const handleSuccessPopin = offerId => {
    dispatch(closeSharePopin())
    const successUrl = `${pathname}/confirmation${search}`
    ownProps.tracking.trackEvent({ action: 'cancelBooking', name: offerId })
    history.push(successUrl)
  }

  const cancelBooking = (bookingId, offerId) => {
    dispatch(
      requestData({
        apiPath: `/bookings/${bookingId}/cancel`,
        handleFail: handleOpenFailurePopin,
        handleSuccess: () => handleSuccessPopin(offerId),
        method: 'PUT',
        normalizer: bookingNormalizer,
      })
    )
  }

  return {
    openCancelPopin: (bookingId, offerName, offerId) => {
      function yesButtonAction() {
        cancelBooking(bookingId, offerId)
      }

      const yesButton = (
        <PopinButton
          action={yesButtonAction}
          label="Oui"
        />
      )

      const noButton = (
        <PopinButton
          action={handleClosePopinAction}
          label="Non"
        />
      )
      const options = {
        buttons: [yesButton, noButton],
        handleClose: () => history.push(`${pathname.split('/reservation/')[0]}${search}`),
        text: 'Souhaites-tu réellement annuler cette réservation ?',
        title: offerName,
      }
      dispatch(openSharePopin(options))
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(mapStateToProps, mapDispatchToProps)
)(CancellingAction)
