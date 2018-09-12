import { Icon, requestData } from 'pass-culture-shared'
import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Price from '../layout/Price'
import Thumb from '../layout/Thumb'
import aggregatedStockSelector from '../../selectors/aggregatedStock'
import eventSelector from '../../selectors/event'
import maxDateSelector from '../../selectors/maxDate'
import mediationsSelector from '../../selectors/mediations'
import eventOccurrencesSelector from '../../selectors/eventOccurrences'
import stocksSelector from '../../selectors/stocks'
import thingSelector from '../../selectors/thing'
import thumbUrlSelector from '../../selectors/thumbUrl'
import typeSelector from '../../selectors/type'
import { offerNormalizer } from '../../utils/normalizers'
import { pluralize } from '../../utils/string'

class OccasionItem extends Component {
  onDeactivateClick = event => {
    const { offer, requestData } = this.props
    const { id, isActive } = offer || {}
    requestData('PATCH', `offers/${id}`, {
      body: {
        offer: {
          isActive: !isActive,
        },
      },
      key: 'offers',
      normalizer: offerNormalizer,
      isMergingDatum: true,
      isMutatingDatum: true,
      isMutaginArray: false,
    })
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
      type,
    } = this.props
    const { isNew } = offer || {}
    const { available, groupSizeMin, groupSizeMax, priceMin, priceMax } =
      aggregatedStock || {}
    const { name, createdAt, isActive } = event || thing || {}

    const mediationsLength = get(mediations, 'length')

    return (
      <li className={classnames('offer-item', { active: isActive })}>
        <Thumb alt="offre" src={thumbUrl} />
        <div className="list-content">
          <NavLink
            className="name"
            to={`/offres/${offer.id}${search}`}
            title={name}>
            <Dotdotdot clamp={1}>{name}</Dotdotdot>
          </NavLink>
          <ul className="infos">
            {isNew && (
              <li>
                <div className="recently-added" />
              </li>
            )}
            {false &&
              moment(createdAt).isAfter(moment().add(-1, 'days')) && (
                <li>
                  <div className="recently-added" />
                </li>
              )}
            <li className="is-uppercase">
              {get(type, 'label') || (event ? 'Evénement' : 'Objet')}
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
            <li
              title={
                groupSizeMin > 0
                  ? groupSizeMin === groupSizeMax
                    ? `minimum ${pluralize(groupSizeMin, 'personnes')}`
                    : `entre ${groupSizeMin} et ${groupSizeMax} personnes`
                  : undefined
              }>
              {groupSizeMin === 0 && (
                <div>
                  <Icon svg="picto-user" /> {'ou '} <Icon svg="picto-group" />
                </div>
              )}
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
                className={`button is-small ${
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
              <button
                className="button is-secondary is-small"
                onClick={this.onDeactivateClick}>
                {isActive ? (
                  <span>
                    <Icon svg="ico-close-r" />
                    Désactiver
                  </span>
                ) : (
                  'Activer'
                )}
              </button>
              <NavLink
                to={`/offres/${offer.id}`}
                className="button is-secondary is-small">
                <Icon svg="ico-pen-r" />
              </NavLink>
            </li>
          </ul>
        </div>
      </li>
    )
  }
}

OccasionItem.defaultProps = {
  maxDescriptionLength: 300,
}

export default compose(
  withRouter,
  connect(
    () => {
      return (state, ownProps) => {
        const { id, eventId, thingId, venueId } = ownProps.offer
        const event = eventSelector(state, eventId)
        const thing = thingSelector(state, thingId)
        const typeValue = get(event, 'type') || get(thing, 'type')
        const eventOccurrences = eventOccurrencesSelector(state, id)
        return {
          aggregatedStock: aggregatedStockSelector(state, id, eventOccurrences),
          event: event,
          eventOccurrences,
          maxDate: maxDateSelector(state, id),
          mediations: mediationsSelector(state, id),
          stocks: stocksSelector(state, id, eventOccurrences),
          thing: thing,
          thumbUrl: thumbUrlSelector(state, id, eventId, thingId),
          type: typeSelector(state, typeValue),
        }
      }
    },
    { requestData }
  )
)(OccasionItem)
