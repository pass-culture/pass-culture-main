import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Price from './Price'
import Icon from './layout/Icon'
import Thumb from './layout/Thumb'
import eventSelector from '../selectors/event'
import maxDateSelector from '../selectors/maxDate'
import mediationsSelector from '../selectors/mediations'
import occurencesSelector from '../selectors/occurences'
import stockSelector from '../selectors/stock'
import thingSelector from '../selectors/thing'
import thumbUrlSelector from '../selectors/thumbUrl'
import typeSelector from '../selectors/type'
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
            <li>{available ? `${pluralize('restent', available)} ${available}` : '0 place'} </li>
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
      return (state, ownProps) => {
        const {eventId, thingId, venueId} = ownProps.occasion
        return {
          event: eventSelector(state, eventId),
          mediations: mediationsSelector(state, eventId, thingId),
          occurences: occurencesSelector(state, venueId, eventId),
          maxDate: maxDateSelector(state, venueId, eventId),
          stock: stockSelector(state, venueId, eventId),
          thing: thingSelector(state, thingId),
          thumbUrl: thumbUrlSelector(state, eventId, thingId),
          type: typeSelector(state, eventId, thingId)
        }
      }
    },
    { requestData }
  )
)(OccasionItem)
