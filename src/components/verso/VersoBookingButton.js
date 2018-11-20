/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link, withRouter } from 'react-router-dom'

import Price from '../layout/Price'
import Finishable from '../layout/Finishable'
import { isRecommendationFinished } from '../../helpers'
import { selectBookings } from '../../selectors/selectBookings'
import currentRecommendation from '../../selectors/currentRecommendation'

class VersoBookingButton extends React.PureComponent {
  renderBookingLink = () => {
    const { offer, url } = this.props
    const priceValue = get(offer, 'price') || get(offer, 'displayPrice')
    return (
      <Link to={`${url}/booking`} className="button is-primary is-medium">
        <Price free="——" value={priceValue} />
        <span>J&apos;y vais!</span>
      </Link>
    )
  }

  renderOfflineButton = () => (
    <Link to="/reservations" className="button is-primary is-medium">
      Réservé
    </Link>
  )

  renderOnlineButton = () => {
    const { booking } = this.props
    const onlineOfferUrl = get(booking, 'completedUrl')
    return (
      <a
        href={`${onlineOfferUrl}`}
        target="_blank"
        rel="noopener noreferrer"
        className="button is-primary is-medium"
      >
        Accéder
      </a>
    )
  }

  render() {
    const { booking, isFinished } = this.props
    const onlineOfferUrl = get(booking, 'completedUrl')
    return (
      <React.Fragment>
        {booking && onlineOfferUrl && this.renderOnlineButton()}
        {booking && !onlineOfferUrl && this.renderOfflineButton()}
        {!booking && !isFinished && this.renderBookingLink()}
        {!booking && isFinished && (
          <Finishable finished>{this.renderBookingLink()}</Finishable>
        )}
      </React.Fragment>
    )
  }
}

VersoBookingButton.defaultProps = {
  booking: null,
  isFinished: false,
  offer: null,
}

VersoBookingButton.propTypes = {
  booking: PropTypes.object,
  isFinished: PropTypes.bool,
  offer: PropTypes.object,
  url: PropTypes.string.isRequired,
}

const mapStateToProps = (state, { match }) => {
  const { params, url } = match
  const { mediationId, offerId } = params
  const recommendation = currentRecommendation(state, offerId, mediationId)
  const isFinished = isRecommendationFinished(recommendation, offerId)
  // NOTE -> on ne peut pas faire confiance a bookingsIds
  // bookingsIds n'est pas mis à jour avec le state
  const stocks = get(recommendation, 'offer.stocks')
  const stockIds = (stocks || []).map(o => o.id)
  const bookings = selectBookings(state)
  const booking = bookings.find(b => stockIds.includes(b.stockId))
  return {
    booking,
    isFinished,
    offer: recommendation.offer,
    url,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoBookingButton)
