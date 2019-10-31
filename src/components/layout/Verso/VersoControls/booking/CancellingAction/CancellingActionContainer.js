import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import withTracking from '../../../../../hocs/withTracking'
import CancellingAction from './CancellingAction'
import PopinButton from './PopinButton'
import { bookingNormalizer } from '../../../../../../utils/normalizers'
import { closeSharePopin, openSharePopin } from '../../../../../../reducers/share'
import { selectBookingByRouterMatch } from '../../../../../../selectors/data/bookingsSelector'
import { selectOfferByRouterMatch } from '../../../../../../selectors/data/offersSelector'
import selectStockById from '../../../../../../selectors/selectStockById'

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

  return { booking, cancellingUrl, offer, price }
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
          action: handleClosePopin,
          label: 'OK',
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
            action: () => requestPatchBooking(bookingId, offerId),
            label: 'Oui',
          }),
          PopinButton({
            action: handleClosePopin,
            label: 'Non',
          }),
        ],
        handleClose: () => history.push(`${pathname.split('/reservation/')[0]}${search}`),
        text: 'Souhaitez-vous réellement annuler cette réservation ?',
        title: offerName,
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
)(CancellingAction)
