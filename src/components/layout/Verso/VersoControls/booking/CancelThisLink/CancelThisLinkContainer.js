import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import CancelThisLink from './CancelThisLink'
import PopinButton from './PopinButton'
import { closeSharePopin, openSharePopin } from '../../../../../../reducers/share'
import selectBookingByRouterMatch from '../../../../../../selectors/selectBookingByRouterMatch'
import selectOfferByMatch from '../../../../../../selectors/selectOfferByMatch'
import selectStockById from '../../../../../../selectors/selectStockById'
import selectIsFinishedByRouterMatch from '../../../../../../selectors/selectIsFinishedByRouterMatch'
import { bookingNormalizer } from '../../../../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const booking = selectBookingByRouterMatch(state, match)
  const offer = selectOfferByMatch(state, match)
  const isBookingFinished = selectIsFinishedByRouterMatch(state, match)
  const stock = selectStockById(state, booking.stockId)

  return { booking, isBookingFinished, offer, stock }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { history, location } = ownProps
  const { pathname, search } = location

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
          onClick: () => dispatch(closeSharePopin()),
        }),
      ],
      text: message.join('\n'),
      title: 'Annulation impossible',
    }
    dispatch(openSharePopin(options))
  }

  const handleSuccessPopin = () => {
    dispatch(closeSharePopin())
    const successUrl = `${pathname}/confirmation${search}`
    history.push(successUrl)
  }

  const requestPatchBooking = bookingId => {
    dispatch(
      requestData({
        apiPath: `/bookings/${bookingId}`,
        body: { isCancelled: true },
        handleFail: handleOpenFailurePopin,
        handleSuccess: handleSuccessPopin,
        method: 'PATCH',
        normalizer: bookingNormalizer,
      })
    )
  }

  const handleClosePopin = () => {
    dispatch(closeSharePopin())
    const nextPathname = pathname.split(/\/reservation(\/|$|\/$)/)[0]
    const nextUrl = `${nextPathname}${search}`
    history.push(nextUrl)
  }

  return {
    openCancelPopin: (bookingId, offerName) => {
      const options = {
        buttons: [
          PopinButton({
            id: 'popin-cancel-booking-yes',
            label: 'Oui',
            onClick: () => requestPatchBooking(bookingId),
          }),
          PopinButton({
            id: 'popin-cancel-booking-no',
            label: 'Non',
            onClick: handleClosePopin,
          }),
        ],
        text: 'Souhaitez-vous réellement annuler cette réservation ?',
        offerName,
      }
      dispatch(openSharePopin(options))
    },
  }
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(CancelThisLink)
