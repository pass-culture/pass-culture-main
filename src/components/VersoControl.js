/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import { Logger, Icon, requestData, showModal } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Booking from './Booking'
import BookingControlButton from './BookingControlButton'
import { selectBookings } from '../selectors/selectBookings'
import currentRecommendationSelector from '../selectors/currentRecommendation'

class VersoControl extends Component {
  onClickDisable = event => {
    alert('Pas encore disponible')
    event.preventDefault()
  }

  onClickFavorite = () => {
    const { recommendation, dispatchRequestData } = this.props
    const { id, isFavorite } = recommendation
    const body = { isFavorite: !isFavorite }
    dispatchRequestData('PATCH', `currentRecommendations/${id}`, {
      body,
      key: 'currentRecommendations',
    })
  }

  onClickShare = () => {
    // TODO
  }

  onClickJyVais = () => {
    const { recommendation, offer, dispatchShowModal } = this.props
    const { isFinished } = recommendation || {}

    if (isFinished) return
    if (offer) {
      dispatchShowModal(<Booking />, {
        fullscreen: true,
        hasCloseButton: false,
        maskColor: 'transparent',
      })
    } else {
      alert("Ce bouton vous permet d'effectuer une reservation")
    }
  }

  render() {
    const { bookings, offer, recommendation, match } = this.props
    const { isFinished } = recommendation || {}
    const isFavorite = recommendation && recommendation.isFavorite
    Logger.fixme('VersoControl is mounted but not visible')
    return (
      <ul className="verso-control">
        <li>
          <small className="pass-label">Mon Pass</small>
          <span className="pass-value">——€</span>
        </li>
        <li>
          <button
            type="button"
            className="button is-secondary"
            onClick={this.onClickFavorite}
          >
            <Icon
              alt={isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
              svg={isFavorite ? 'ico-like-w-on' : 'ico-like-w'}
            />
          </button>
        </li>
        <li>
          <button
            type="button"
            disabled
            className="button is-secondary"
            onClick={this.onClickDisable}
          >
            <Icon svg="ico-share-w" alt="Partager" />
          </button>
        </li>
        <li>
          <BookingControlButton
            offer={offer}
            matchURL={match.url}
            isFinished={isFinished}
            isAlreadyBooked={bookings.length > 0}
          />
        </li>
      </ul>
    )
  }
}

VersoControl.defaultProps = {
  offer: null,
  recommendation: null,
}

VersoControl.propTypes = {
  bookings: PropTypes.array.isRequired,
  dispatchRequestData: PropTypes.func.isRequired,
  dispatchShowModal: PropTypes.func.isRequired,
  match: PropTypes.object.isRequired,
  offer: PropTypes.object,
  recommendation: PropTypes.object,
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { mediationId, offerId } = ownProps.match.params
      const recommendation = currentRecommendationSelector(
        state,
        offerId,
        mediationId
      )
      const eventOrThingId = get(recommendation, 'offer.eventOrThing.id')
      console.log('recommendation', recommendation)
      console.log('eventOrThingId', eventOrThingId)
      return {
        bookings: selectBookings(state, eventOrThingId),
        recommendation,
      }
    },
    {
      dispatchRequestData: requestData,
      dispatchShowModal: showModal,
    }
  )
)(VersoControl)
