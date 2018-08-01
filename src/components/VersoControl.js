import get from 'lodash.get'
import {
  Icon,
  requestData,
  showModal
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Link } from 'react-router-dom'
import { compose } from 'redux'

import Price from './Price'
import Booking from './Booking'
import Finishable from './layout/Finishable'
import bookingsSelector from '../selectors/bookings'
import currentRecommendationSelector from '../selectors/currentRecommendation'

class VersoControl extends Component {
  onClickDisable = event => {
    alert('Pas encore disponible')
    event.preventDefault()
  }

  onClickFavorite = () => {
    const { currentRecommendation, requestData } = this.props
    const { id, isFavorite } = currentRecommendation
    requestData('PATCH', `currentRecommendations/${id}`, {
      body: {
        isFavorite: !isFavorite,
      },
      key: 'currentRecommendations',
    })
  }

  onClickShare = () => {
    // TODO
  }

  onClickJyVais = event => {
    const {
      currentRecommendation,
      offer,
      showModal
    } = this.props
    const {
      isFinished
    } = (currentRecommendation || {})

    if (isFinished) return
    if (offer) {
      showModal(<Booking />, {
        fullscreen: true,
        maskColor: 'transparent',
        hasCloseButton: false,
      })
    } else {
      alert("Ce bouton vous permet d'effectuer une reservation")
    }
  }

  render() {
    const {
      bookings,
      offer,
      currentRecommendation
    } = this.props
    const {
      isFinished
    } = (currentRecommendation || {})
    const {
      venue
    } = (offer || {})
    const {
      managingOfferer
    } = (venue || {})
    const isFavorite = currentRecommendation && currentRecommendation.isFavorite
    return (
      <ul className="verso-control">
        <li>
          <small className="pass-label">
            Mon Pass
          </small>
          <span className="pass-value">
            ——€
          </span>
        </li>
        <li>
          <button
            className="button is-secondary"
            onClick={this.onClickFavorite}>
            <Icon
              alt={isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
              svg={isFavorite ? 'ico-like-w-on' : 'ico-like-w'}
            />
          </button>
        </li>
        <li>
          <button
            disabled
            className="button is-secondary"
            onClick={this.onClickDisable}>
            <Icon svg="ico-share-w" alt="Partager" />
          </button>
        </li>
        <li>
          {bookings.length > 0 ? (
            <Link
              to="/reservations"
              className="button is-primary is-go is-medium">
              <Icon name="Check" />
              {' Réservé'}
            </Link>
          ) : (
            <Finishable finished={isFinished}>
              <button
                className="button is-primary is-go is-medium"
                onClick={this.onClickJyVais}>
                <Price
                  value={get(offer, 'price') || get(offer, 'displayPrice')}
                  free="——"
                  className={managingOfferer ? 'strike' : ''}
                />
                J'y vais!
              </button>
            </Finishable>
          )}
        </li>
      </ul>
    )
  }
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    const currentRecommendation = currentRecommendationSelector(state, offerId, mediationId)
    const eventOrThingId = get(currentRecommendation, 'offer.eventOrThing.id')
    return {
      bookings: bookingsSelector(state, eventOrThingId),
      currentRecommendation
    }
  },
  {
    requestData,
    showModal,
  })
)(VersoControl)
