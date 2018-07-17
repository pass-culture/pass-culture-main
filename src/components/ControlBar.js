import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import Price from './Price'
import Booking from './Booking'
import Finishable from './layout/Finishable'
import Icon from './layout/Icon'
import selectBookings from '../selectors/bookings'
import selectCurrentEventOrThingId from '../selectors/currentEventOrThingId'
import selectCurrentOffer from '../selectors/currentOffer'
import selectCurrentOfferer from '../selectors/currentOfferer'
import selectCurrentRecommendation from '../selectors/currentRecommendation'
import selectIsFinished from '../selectors/isFinished'
import { requestData } from '../reducers/data'
import { showModal } from '../reducers/modal'
import { IS_DEXIE } from '../utils/config'


class ControlBar extends Component {
  onClickDisable = event => {
    alert('Pas encore disponible')
    event.preventDefault()
  }

  onClickFavorite = () => {
    const { recommendation, requestData } = this.props
    const { id, isFavorite } = recommendation
    requestData('PATCH', `recommendations/${id}`, {
      body: {
        isFavorite: !isFavorite,
      },
      local: IS_DEXIE,
      key: 'recommendations'
    })
  }

  onClickShare = () => {
    // TODO
  }

  onClickJyVais = event => {
    if (this.props.isFinished) return
    if (this.props.offer) {
      this.props.showModal(<Booking />, {
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
      offerer,
      recommendation
    } = this.props
    const isFavorite = recommendation && recommendation.isFavorite
    return (
      <ul className="control-bar">
        <li>
          <small className="pass-label">Mon Pass</small>
          <span className="pass-value">——€</span>
        </li>
        <li>
          <button
            className="button is-secondary"
            onClick={this.onClickFavorite}
          >
            <Icon
              alt={isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris' }
              svg={isFavorite ? 'ico-like-w-on' : 'ico-like-w'}
            />
          </button>
        </li>
        <li>
          <button
            disabled
            className="button is-secondary"
            onClick={this.onClickDisable}
          >
            <Icon svg="ico-share-w" alt='Partager' />
          </button>
        </li>
        <li>
          {bookings.length > 0 ? (
            <Link
              to="/reservations"
              className="button is-primary is-go is-medium"
            >
              <Icon name="Check" />
              {' Réservé'}
            </Link>
          ) : (
            <Finishable finished={this.props.isFinished}>
              <button
                className="button is-primary is-go is-medium"
                onClick={this.onClickJyVais}
              >
                <Price
                  value={get(offer, 'price') || get(offer, 'displayPrice')}
                  free="——"
                  className={offerer ? 'strike' : ''}
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

export default connect(
  function (state) {
    const eventOrThingId = selectCurrentEventOrThingId(state)
    return {
      bookings: selectBookings(state, eventOrThingId),
      isFinished: selectIsFinished(state),
      offer: selectCurrentOffer(state),
      offerer: selectCurrentOfferer(state),
      recommendation: selectCurrentRecommendation(state),
    }
  },
  {
    requestData,
    showModal,
  }
)(ControlBar)
