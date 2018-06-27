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
import createEventSelector from '../selectors/createEvent'
import createMaxDateSelector from '../selectors/createMaxDate'
import createMediationsSelector from '../selectors/createMediations'
import createOccurencesSelector from '../selectors/createOccurences'
import createStockSelector from '../selectors/createStock'
import createThingSelector from '../selectors/createThing'
import createThumbUrlSelector from '../selectors/createThumbUrl'
import createTypeSelector from '../selectors/createType'
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

  onDeleteClick = () => {
    const {
      occasion,
      requestData,
    } = this.props
    requestData('DELETE', `occasions/${occasion.id}`, { key: 'occasions' })
  }

  render() {
    const {
      event,
      location: { search },
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
      maxDate,
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
            {moment(createdAt).isAfter(moment().add(-1, 'days')) && <li><div className='recently-added'></div></li>}
            <li className='is-uppercase'>{get(type, 'label')}</li>
            <li>
              <NavLink className='has-text-primary' to={`/offres/${occasion.id}/dates${search}`}>
                {pluralize(get(occurences, 'length'), 'dates')}
              </NavLink>
            </li>
            <li>{maxDate && `jusqu'au ${maxDate.format('DD/MM/YYYY')}`}</li>
            {groupSizeMin > 0 && <li>{groupSizeMin === groupSizeMax ? `minimum ${pluralize(groupSizeMin, 'personnes')}` : `entre ${groupSizeMin} et ${groupSizeMax} personnes`}</li>}
            {available > 0 && <li>{pluralize(available, 'places restantes')}</li>}
            <li>{priceMin === priceMax ? <Price value={priceMin} /> : (<span><Price value={priceMin} /> - <Price value={priceMax} /></span>)}</li>
          </ul>
          <ul className='actions'>
            <li>
              <NavLink  to={`offres/${occasion.id}${mediationsLength ? '' : '/accroches/nouveau${search}'}`}
                className={`button is-small ${mediationsLength ? 'is-secondary' : 'is-primary is-outlined'}`}>
                <span className='icon'><Icon svg='ico-stars' /></span>
                <span>{get(mediations, 'length') ? 'Accroches' : 'Ajouter une Accroche'}</span>
              </NavLink>
            </li>
            <li>
              <button className='button is-secondary is-small'
                onClick={this.onDeactivateClick}>
                {isActive ? ('X Désactiver') : ('Activer')}
              </button>
              <NavLink  to={`offres/${occasion.id}`} className="button is-secondary is-small">
                <Icon svg='ico-pen-r' />
              </NavLink>
            </li>
          </ul>
        </div>
        {false && <div className="is-pulled-right" key={2}>
                  <button className="delete is-small"
                    onClick={this.onDeleteClick} />
                </div>}
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
      const eventSelector = createEventSelector()
      const mediationsSelector = createMediationsSelector()
      const occurencesSelector = createOccurencesSelector()
      const thingSelector = createThingSelector()
      const typeSelector = createTypeSelector(eventSelector, thingSelector)

      const maxDateSelector = createMaxDateSelector(occurencesSelector)
      const stockSelector = createStockSelector(occurencesSelector)
      const thumbUrlSelector = createThumbUrlSelector(mediationsSelector)

      return (state, ownProps) => {
        const occasion = ownProps.occasion
        const event = eventSelector(state, occasion.eventId)
        const thing = thingSelector(state, occasion.thingId)
        return {
          event,
          mediations: mediationsSelector(state, event, thing),
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
