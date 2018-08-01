import get from 'lodash.get'
import { requestData, showModal } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Link } from 'react-router-dom'
import { compose } from 'redux'

import Price from './Price'
import Booking from './Booking'
import Finishable from './layout/Finishable'
import Icon from './layout/Icon'
import selectBookings from '../selectors/bookings'
import selectCurrentEventOrThingId from '../selectors/currentEventOrThingId'
import currentRecommendation from '../selectors/currentRecommendation'
import selectIsFinished from '../selectors/isFinished'
import { IS_DEXIE } from '../utils/config'

class ControlBar extends Component {
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
      local: IS_DEXIE,
      key: 'currentRecommendations',
    })
  }

  onClickShare = () => {
    // TODO
  }

  onClickJyVais = event => {
    const {
      isFinished,
      offer,
      showModal
    } = this.props

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
      offerer,
      currentRecommendation
    } = this.props
    const isFavorite = currentRecommendation && currentRecommendation.isFavorite
    return (
      <ul className="control-bar">
        <li>
          <small className="pass-label">Mon Pass</small>
          <span className="pass-value">——€</span>
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
            <Finishable finished={this.props.isFinished}>
              <button
                className="button is-primary is-go is-medium"
                onClick={this.onClickJyVais}>
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

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const eventOrThingId = selectCurrentEventOrThingId(state)
    const { mediationId, offerId } = ownProps.match.params
    return {
      bookings: selectBookings(state, eventOrThingId),
      currentRecommendation: currentRecommendation(state, offerId, mediationId),
      isFinished: selectIsFinished(state),
    }
  },
  {
    requestData,
    showModal,
  })
)(ControlBar)
