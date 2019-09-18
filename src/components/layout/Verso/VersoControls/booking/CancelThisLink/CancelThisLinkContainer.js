import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import withTracking from '../../../../../hocs/withTracking'
import CancelThisLink from './CancelThisLink'
import PopinButton from './PopinButton'

import { bookingNormalizer } from '../../../../../../utils/normalizers'
import { closeSharePopin, openSharePopin } from '../../../../../../reducers/share'
import selectBookingByRouterMatch from '../../../../../../selectors/selectBookingByRouterMatch'
import selectOfferByRouterMatch from '../../../../../../selectors/selectOfferByRouterMatch'
import selectStockById from '../../../../../../selectors/selectStockById'
import selectIsFinishedByRouterMatch from '../../../../../../selectors/selectIsFinishedByRouterMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const booking = selectBookingByRouterMatch(state, match)
  const offer = selectOfferByRouterMatch(state, match)
  const isBookingFinished = selectIsFinishedByRouterMatch(state, match)
  const stock = selectStockById(state, booking.stockId)

  return { booking, isBookingFinished, offer, stock }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { history, location } = ownProps
  const { pathname, search } = location

  const handleClosePopin = () => {
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
      buttons: [
        PopinButton({
          id: 'popin-cancel-booking-fail-ok',
          label: 'OK',
          onClick: handleClosePopin,
        }),
      ],
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

  const requestPatchBooking = (bookingId, offerId) => {
    dispatch(
      requestData({
        apiPath: `/bookings/${bookingId}`,
        body: { isCancelled: true },
        handleFail: handleOpenFailurePopin,
        handleSuccess: () => handleSuccessPopin(offerId),
        method: 'PATCH',
        normalizer: bookingNormalizer,
      })
    )
  }

  return {
    openCancelPopin: (bookingId, offerName, offerId) => {
      const options = {
        buttons: [
          PopinButton({
            id: 'popin-cancel-booking-yes',
            label: 'Oui',
            onClick: () => requestPatchBooking(bookingId, offerId),
          }),
          PopinButton({
            id: 'popin-cancel-booking-no',
            label: 'Non',
            onClick: handleClosePopin,
          }),
        ],
        text: 'Souhaitez-vous réellement annuler cette réservation ?',
        offerName,
        withCloseButton: false,
      }
      dispatch(openSharePopin(options))
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(CancelThisLink)
