import { Icon, pluralize, requestData } from 'pass-culture-shared'
import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { NavLink } from 'react-router-dom'

import Price from '../../layout/Price'
import Thumb from '../../layout/Thumb'

import { offerNormalizer } from '../../../utils/normalizers'

class RawOfferItem extends Component {
  onDeactivateClick = event => {
    const { dispatch, offer } = this.props
    const { id, isActive } = offer || {}
    dispatch(
      requestData('PATCH', `offers/${id}`, {
        body: {
          isActive: !isActive,
        },
        normalizer: offerNormalizer,
        isMergingDatum: true,
        isMutatingDatum: true,
        isMutaginArray: false,
      })
    )
  }

  render() {
    const {
      aggregatedStock,
      event,
      eventOccurrences,
      location: { search },
      maxDate,
      mediations,
      offer,
      stocks,
      thing,
      thumbUrl,
      offerTypeLabel,
      offerrer,
      venue,
    } = this.props

    const { isNew } = offer || {}
    const { available, groupSizeMin, groupSizeMax, priceMin, priceMax } =
      aggregatedStock || {}
    const { name, createdAt } = event || thing || {}

    const mediationsLength = get(mediations, 'length')

    return (
      <li
        className={classnames('offer-item', {
          active: offer.isActive,
          event,
          thing,
        })}>
        <Thumb alt="offre" src={thumbUrl} />
        <div className="list-content">
          <NavLink
            className="name"
            to={`/offres/${offer.id}${search}`}
            title={name}>
            <Dotdotdot clamp={1}>{name}</Dotdotdot>
          </NavLink>
          <ul className="infos">
            <li className="is-uppercase">{offerTypeLabel}</li>
            <li>
              <span className="label">Structure :</span>
              {offerrer && offerrer.name}
            </li>
            <li>
              <span className="label">Lieu :</span> {venue && venue.name}
            </li>
          </ul>
          <ul className="infos">
            {isNew && (
              <li>
                <div className="recently-added" />
              </li>
            )}
            {false && moment(createdAt).isAfter(moment().add(-1, 'days')) && (
              <li>
                <div className="recently-added" />
              </li>
            )}
            <li
              title={
                groupSizeMin > 0
                  ? groupSizeMin === groupSizeMax
                    ? `minimum ${pluralize(groupSizeMin, 'personnes')}`
                    : `entre ${groupSizeMin} et ${groupSizeMax} personnes`
                  : undefined
              }>
              {
                // DISABLE GROUP SIZE AMBIGUITY FOR THE MOMENT
                /*groupSizeMin === 0 && (
                <div>
                  <Icon svg="picto-user" /> {'ou '} <Icon svg="picto-group" />
                </div>
                )*/
              }
              {groupSizeMin === 1 && <Icon svg="picto-user" />}
              {groupSizeMin > 1 && (
                <div>
                  <Icon svg="picto-group" />,{' '}
                  <p>
                    {groupSizeMin === groupSizeMax
                      ? groupSizeMin
                      : `${groupSizeMin} - ${groupSizeMax}`}
                  </p>
                </div>
              )}
            </li>
            <li>
              <NavLink
                className="has-text-primary"
                to={`/offres/${offer.id}?gestion`}>
                {event
                  ? pluralize(get(eventOccurrences, 'length'), 'dates')
                  : get(stocks, 'length') + ' prix'}
              </NavLink>
            </li>
            <li>{maxDate && `jusqu'au ${maxDate.format('DD/MM/YYYY')}`}</li>
            <li>{available ? `encore ${available} places` : '0 place'} </li>
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
                to={`/offres/${offer.id}${
                  mediationsLength ? '' : `/accroches/nouveau${search}`
                }`}
                className={`button addMediations is-small ${
                  mediationsLength ? 'is-secondary' : 'is-primary is-outlined'
                }`}>
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
                to={`/offres/${offer.id}`}
                className="button is-secondary is-small edit-link">
                <Icon svg="ico-pen-r" />
                Modifier
              </NavLink>

              <button
                className="button is-secondary is-small activ-switch"
                onClick={this.onDeactivateClick}>
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

RawOfferItem.defaultProps = {
  maxDescriptionLength: 300,
}
export default RawOfferItem
