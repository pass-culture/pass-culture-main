import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Price from './Price'
import Icon from './layout/Icon'
import Thumb from './layout/Thumb'
import { requestData } from '../reducers/data'
import eventSelector from '../selectors/event'
import maxDateSelector from '../selectors/maxDate'
import mediationsSelector from '../selectors/mediations'
import createOccurencesSelector from '../selectors/createOccurences'
import createOffersSelector from '../selectors/createOffers'
import createStockSelector from '../selectors/createStock'
import createThingSelector from '../selectors/createThing'
import createThumbUrlSelector from '../selectors/createThumbUrl'
import createTypeSelector from '../selectors/createType'
import createTypesSelector from '../selectors/createTypes'
import { occasionNormalizer } from '../utils/normalizers'
import { pluralize } from '../utils/string'



class OccasionItem extends Component {

  onDeactivateClick = event => {
    const {
      occasion,
      requestData
    } = this.props
    const {
      id,
      isActive,
    } = (occasion || {})
    requestData(
      'PATCH',
      `occasions/${id}`,
        {
          body: {
            occasion: {
              isActive: !isActive
            }
          },
          key: 'occasions',
          normalizer: occasionNormalizer,
          isMergingDatum: true,
          isMutatingDatum: true,
          isMutaginArray: false
        }
      )
  }

  render() {
    const {
      event,
      location: { search },
      maxDate,
      mediations,
      occasion,
      occurences,
      stock,
      thing,
      thumbUrl,
      type,
    } = this.props
    const {
      available,
      groupSizeMin,
      groupSizeMax,
      priceMin,
      priceMax,
    } = (stock || {})
    const {
      name,
      createdAt,
      isActive,
    } = (event || thing || {})

    const mediationsLength = get(mediations, 'length')

    return (
      <li className={classnames('occasion-item', { active: isActive })}>
        <Thumb alt='offre' src={thumbUrl} />
        <div className="list-content">
          <NavLink className='name' to={`/offres/${occasion.id}${search}`} title={name}>
            <Dotdotdot clamp={1}>{name}</Dotdotdot>
          </NavLink>
          <ul className='infos'>
            {false && moment(createdAt).isAfter(moment().add(-1, 'days')) && <li><div className='recently-added'></div></li>}
            <li className='is-uppercase'>{get(type, 'label') || (event ? 'Evénement' : 'Objet')}</li>
            {event &&
              <li>
                <NavLink className='has-text-primary' to={`/offres/${occasion.id}/dates${search}`}>
                  {pluralize(get(occurences, 'length'), 'dates')}
                </NavLink>
              </li>
            }
            <li>{maxDate && `jusqu'au ${maxDate.format('DD/MM/YYYY')}`}</li>
            <li title={groupSizeMin > 0 ? (groupSizeMin === groupSizeMax ? `minimum ${pluralize(groupSizeMin, 'personnes')}` : `entre ${groupSizeMin} et ${groupSizeMax} personnes`) : undefined}>
              {groupSizeMin === 0 && <div><Icon svg='picto-user' /> {'ou '} <Icon svg='picto-group' /></div>}
              {groupSizeMin === 1 && <Icon svg='picto-user' />}
              {groupSizeMin > 1 && <div><Icon svg='picto-group' />, <p>{groupSizeMin === groupSizeMax ? groupSizeMin : `${groupSizeMin} - ${groupSizeMax}`}</p></div>}
            </li>
            <li>{available ? `${pluralize('restent', available)} ${available}` : 'Places illimitées'} </li>
            <li>{priceMin === priceMax ? <Price value={priceMin || 0} /> : (<span><Price value={priceMin} /> - <Price value={priceMax} /></span>)}</li>
          </ul>
          <ul className='actions'>
            <li>
              <NavLink  to={`offres/${occasion.id}${mediationsLength ? '' : `/accroches/nouveau${search}`}`}
                className={`button is-small ${mediationsLength ? 'is-secondary' : 'is-primary is-outlined'}`}>
                <span className='icon'><Icon svg='ico-stars' /></span>
                <span>{get(mediations, 'length') ? 'Accroches' : 'Ajouter une Accroche'}</span>
              </NavLink>
            </li>
            <li>
              <button className='button is-secondary is-small'
                onClick={this.onDeactivateClick}>
                {isActive ? <span>
                  <Icon svg='ico-close-r' />
                  Désactiver
                  </span> : ('Activer')}
              </button>
              <NavLink  to={`offres/${occasion.id}`} className="button is-secondary is-small">
                <Icon svg='ico-pen-r' />
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
      const typesSelector = createTypesSelector()
      const thingSelector = createThingSelector()
      const typeSelector = createTypeSelector(typesSelector, eventSelector, thingSelector)
      const thumbUrlSelector = createThumbUrlSelector(mediationsSelector)

      const occurencesSelector = createOccurencesSelector()
      const offersSelector = createOffersSelector(occurencesSelector)

      const stockSelector = createStockSelector(offersSelector)

      return (state, ownProps) => {
        const occasion = ownProps.occasion
        const event = eventSelector(state, occasion.eventId)
        const thing = thingSelector(state, occasion.thingId)
        return {
          event,
          mediations: mediationsSelector(state, occasion.eventId, occasion.thingId),
          occurences: occurencesSelector(state, occasion.venueId, occasion.eventId),
          maxDate: maxDateSelector(state, occasion.venueId, occasion.eventId),
          stock: stockSelector(state, occasion.venueId, occasion.eventId),
          thing,
          thumbUrl: thumbUrlSelector(state, event, thing),
          type: typeSelector(state, occasion.eventId, occasion.thingId)
        }
      }
    },
    { requestData }
  )
)(OccasionItem)
