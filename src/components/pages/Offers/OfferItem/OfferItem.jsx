import classnames from 'classnames'
import get from 'lodash.get'
import { Icon, pluralize } from 'pass-culture-shared'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import Price from 'components/layout/Price'
import Thumb from 'components/layout/Thumb'
import { offerNormalizer } from 'utils/normalizers'


class OfferItem extends Component {
  onDeactivateClick = () => {
    const { dispatch, offer } = this.props
    const { id, isActive } = offer || {}

    dispatch(
      requestData({
        apiPath: `/offers/${id}`,
        body: {
          isActive: !isActive,
        },
        isMergingDatum: true,
        isMutatingDatum: true,
        isMutaginArray: false,
        method: 'PATCH',
        normalizer: offerNormalizer,
      })
    )
  }

  buildNumberOfParticipantsLabel = (groupSizeMin, groupSizeMax) => {
    return groupSizeMin === groupSizeMax
      ? `${groupSizeMin}`
      : `${groupSizeMin} - ${groupSizeMax}`
  }

  buildNumberOfParticipantsTitle = (groupSizeMin, groupSizeMax) => {
    const groupLabel =
      groupSizeMin === groupSizeMax
        ? `minimum ${pluralize(groupSizeMin, 'personnes')}`
        : `entre ${groupSizeMin} et ${groupSizeMax} personnes`

    return groupSizeMin > 0 ? groupLabel : null
  }

  buildProductNavLinkLabel = (offer, stockSize) => {
    if (offer.isThing) {
      return `${stockSize} prix`
    }

    if (offer.isEvent) {
      return pluralize(stockSize, 'date')
    }
  }

  render() {
    const {
      aggregatedStock,
      location: { search },
      maxDate,
      mediations,
      offer,
      product,
      stocks,
      offerTypeLabel,
      offerer,
      stockAlertMessage,
      venue,
    } = this.props

    const { isNew } = offer || {}
    const { groupSizeMin, groupSizeMax, priceMin, priceMax } =
      aggregatedStock || {}
    const { name } = product || {}
    const thumbUrl = offer.activeMediation ? offer.activeMediation.thumbUrl : ''
    const numberOfMediations = get(mediations, 'length')
    const remainingStockQuantity = get(stocks, 'length')

    return (
      <li
        className={classnames('offer-item', {
          active: offer.isActive,
          product,
        })}
      >
        <Thumb
          alt="offre"
          src={thumbUrl}
        />
        <div className="list-content">
          <NavLink
            className="name"
            title={name}
            to={`/offres/${offer.id}${search}`}
          >
            <Dotdotdot clamp={1}>{name}</Dotdotdot>
          </NavLink>
          <ul className="infos">
            <li className="is-uppercase">{offerTypeLabel}</li>
            <li>
              <span className="label">{"Structure : "}</span>
              {offerer && offerer.name}
            </li>
            <li>
              <span className="label">{"Lieu : "}</span>
              {(venue && venue.publicName) || venue.name}
            </li>
          </ul>
          <ul className="infos">
            {isNew && (
              <li>
                <div className="recently-added" />
              </li>
            )}
            <li
              title={this.buildNumberOfParticipantsTitle(
                groupSizeMin,
                groupSizeMax
              )}
            >
              {groupSizeMin === 1 && <Icon svg="picto-user" />}
              {groupSizeMin > 1 && (
                <div>
                  <Icon svg="picto-group" />,{' '}
                  <p>
                    {this.buildNumberOfParticipantsLabel(
                      groupSizeMin,
                      groupSizeMax
                    )}
                  </p>
                </div>
              )}
            </li>
            <li>
              <NavLink
                className="has-text-primary"
                to={`/offres/${offer.id}?gestion`}
              >
                {this.buildProductNavLinkLabel(offer, remainingStockQuantity)}
              </NavLink>
            </li>
            <li>{maxDate && `jusqu'au ${maxDate.format('DD/MM/YYYY')}`}</li>
            {stockAlertMessage && <li>{stockAlertMessage}</li>}
            <li>
              {priceMin === priceMax ? (
                <Price value={priceMin || 0} />
              ) : (
                <span>
                  <Price value={priceMin} /> - <Price value={priceMax} />
                </span>
              )}
            </li>
          </ul>
          <ul className="actions">
            <li>
              <NavLink
                className={`button addMediations is-small ${
                  numberOfMediations ? 'is-secondary' : 'is-primary is-outlined'
                }`}
                to={`/offres/${offer.id}${
                  numberOfMediations ? '' : `/accroches/nouveau${search}`
                }`}
              >
                <span className="icon">
                  <Icon svg="ico-stars" />
                </span>
                <span>
                  {get(mediations, 'length')
                    ? 'Accroches'
                    : 'Ajouter une Accroche'}
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                className="button is-secondary is-small edit-link"
                to={`/offres/${offer.id}`}
              >
                <Icon svg="ico-pen-r" />
                {"Modifier"}
              </NavLink>

              <button
                className="button is-secondary is-small activ-switch"
                onClick={this.onDeactivateClick}
              >
                {offer.isActive ? (
                  <span>
                    <Icon svg="ico-close-r" />
                    Désactiver
                  </span>
                ) : (
                  'Activer'
                )}
              </button>
            </li>
          </ul>
        </div>
      </li>
    )
  }
}

OfferItem.defaultProps = {
  maxDescriptionLength: 300,
}
export default OfferItem
