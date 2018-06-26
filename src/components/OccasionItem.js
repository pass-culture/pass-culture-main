import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Price from './Price'
import Icon from './layout/Icon'
import Thumb from './layout/Thumb'
import { requestData } from '../reducers/data'
import { pluralize } from '../utils/string'
import { occasionNormalizer } from '../utils/normalizers'

import createMediationsSelector from '../selectors/createMediations'
import createOccurencesSelector from '../selectors/createOccurences'

import createEventSelector from '../selectors/createEvent'
import createThingSelector from '../selectors/createThing'

// import createMaxDateSelect from '../selectors/createMaxDate'
// import createStockSelect from '../selectors/createStock'
// import createThumbUrlSelect from '../selectors/thumbUrl'

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
      isActive,
      mediations,
      occasionItem,
      occasion,
      occurences,
      stock,
      thing,
      thumbUrl,
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
      id,
      createdAt,
      eventType,
      name,
    } = (occasion || {})

    const mediationsLength = get(mediations, 'length')
    return (
      <li className={classnames('occasion-item', { active: isActive })}>
        <Thumb alt='offre' src={thumbUrl} />
        <div className="list-content">
          <NavLink className='name' to={`/offres/${id}`} title={name}>
            <Dotdotdot clamp={1}>{name}</Dotdotdot>
          </NavLink>
          <ul className='infos'>
            {moment(createdAt).isAfter(moment().add(-1, 'days')) && <li><div className='recently-added'></div></li>}
            <li className='is-uppercase'>{get(eventType, 'label')}</li>
            <li className='has-text-primary'>{pluralize(get(occurences, 'length'), 'date')}</li>
            <li>{maxDate && `jusqu'au ${maxDate.format('DD/MM/YYYY')}`}</li>
            {groupSizeMin > 0 && <li>{groupSizeMin === groupSizeMax ? groupSizeMin : `entre ${groupSizeMin} et ${groupSizeMax} personnes`}</li>}
            {available > 0 && <li>restent {available}</li>}
            <li>{priceMin === priceMax ? <Price value={priceMin} /> : (<span><Price value={priceMin} /> - <Price value={priceMax} /></span>)}</li>
          </ul>
          <ul className='actions'>
            <li>
              <NavLink  to={`offres/${id}${mediationsLength ? '' : '/accroches/nouveau'}`} className={`button is-small ${mediationsLength ? 'is-secondary' : 'is-primary is-outlined'}`}>
                <span className='icon'><Icon svg='ico-stars' /></span>
                <span>{get(mediations, 'length') ? 'Accroches' : 'Ajouter une Accroche'}</span>
              </NavLink>
            </li>
            <li>
              <button className='button is-secondary is-small' onClick={this.onDeactivateClick}>{isActive ? ('X Désactiver') : ('Activer')}</button>
              <NavLink  to={`offres/${id}`} className="button is-secondary is-small">
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

const eventSelector = createEventSelector()
const thingSelector = createThingSelector()
const mediationsSelector = createMediationsSelector()
const occurencesSelector = createOccurencesSelector()

export default connect(
  () => {
    return (state, ownProps) => {
      const type = ownProps.occasion.modelName === 'Event' ? 'event' : 'thing'
      return {
        event: eventSelector(state, ownProps.occasion.eventId),
        thing: thingSelector(state, ownProps.occasion.thingId),
        mediations: mediationsSelector(state, ownProps), // TODO: replug this
        occurences: occurencesSelector(state, ownProps),
        // TODO: replug this
        // maxDate: createMaxDateSelect()(state, ownProps),
        // stock: createStockSelect()(state, ownProps),
        // thumbUrl: createThumbUrlSelect()(state, ownProps),
      }
    }
  },
  { requestData }
)(OccasionItem)
