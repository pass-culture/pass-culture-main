import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import moment from 'moment'
import classnames from 'classnames'
import get from 'lodash.get'

// import FormInput from './layout/FormInput'
import Icon from './layout/Icon'
import Price from './Price'
import { requestData } from '../reducers/data'
import createSelectOccasionThumbUrl from '../selectors/occasionThumbUrl'
import { modelToPath } from '../utils/translate'

import {API_URL} from '../utils/config'
import {pluralize} from '../utils/string'

class OccasionItem extends Component {

  constructor () {
    super()
    this.state = {
      path: null
    }
  }

  onDeactivateClick = event => {
    const {
      id,
      occasionType,
      requestData
    } = this.props
    requestData(
      'PATCH',
      `occasions/${occasionType}/${id}`,
        {
          body: {
            occasion: {
              isActive: !this.props.isActive
            }
          },
          key: 'occasions',
          isMergingDatum: true,
          isMutatingDatum: true,
          isMutaginArray: false
        }
      )
  }

  static getDerivedStateFromProps (nextProps) {
    return {
      path: `/offres/${modelToPath(nextProps.modelName)}`
    }
  }

  render() {
    const {
      createdAt,
      description,
      id,
      isActive,
      occurences,
      mediations,
      name,
      thumbUrl,
    } = this.props

    const {
      path
    } = this.state

    console.log(this.props)
    const maxDate = occurences.map(o => moment(o.beginningDatetime)).reduce((max, d) => {
      return max && max.isAfter(d) ? max : d
    }, null)
    const {
      available,
      groupSizeMin,
      groupSizeMax,
      priceMin,
      priceMax,
    } = occurences.reduce((aggreged, o) => {
      return o.offer.reduce((subaggreged, offer) => {
        return {
          available: subaggreged.available + offer.available,
          groupSizeMin: subaggreged.groupSizeMin ? Math.min(subaggreged.groupSizeMin, offer.groupSize) : offer.groupSize,
          groupSizeMax: subaggreged.groupSizeMax ? Math.max(subaggreged.groupSizeMax, offer.groupSize) : offer.groupSize,
          priceMin: subaggreged.priceMin ? Math.min(subaggreged.priceMin, offer.price) : offer.price,
          priceMax: subaggreged.priceMax ? Math.max(subaggreged.priceMax, offer.price) : offer.price,
        }
      }, aggreged)
    }, {
      available: 0,
      groupSizeMin: null,
      groupSizeMax: null,
      priceMin: null,
      priceMax: null,
    })
    console.log({
      available,
      groupSizeMin,
      groupSizeMax,
      priceMin,
      priceMax,
    })
    return (
      <li className={classnames('occasion-item', {active: isActive})}>
        <img alt='thumbnail' src={thumbUrl} className="occasion-thumb"/>
        <div className="list-content">
          <NavLink className='name' to={`${path}/${id}`} title={name}>
            <Dotdotdot clamp={1}>{name}</Dotdotdot>
          </NavLink>
          <ul className='infos'>
            {moment(createdAt).isAfter(moment().add(-1, 'days')) && <li><div className='recently-added'></div></li>}
            <li className='is-uppercase'>Théâtre</li>
            <li className='has-text-primary'>{pluralize(occurences.length, 'date')}</li>
            <li>{maxDate && `jusqu'au ${maxDate.format('DD/MM/YYYY')}`}</li>
            {groupSizeMin > 0 && <li>{groupSizeMin === groupSizeMax ? groupSizeMin : `entre ${groupSizeMin} et ${groupSizeMax} personnes`}</li>}
            {available > 0 && <li>restent {available}</li>}
            <li>{priceMin === priceMax ? <Price value={priceMin} /> : (<span><Price value={priceMin} /> - <Price value={priceMax} /></span>)}</li>
          </ul>
          <ul className='actions'>
            <li>
              <NavLink  to={`${path}/${id}${mediations.length ? '' : '/accroches/nouveau'}`} className={`button is-small ${mediations.length ? 'is-secondary' : 'is-primary is-outlined'}`}>
                <span className='icon'><Icon svg='ico-stars' /></span>
                <span>{mediations.length ? 'Accroches' : 'Ajouter une Accroche'}</span>
              </NavLink>
            </li>
            <li>
              <button className='button is-secondary is-small' onClick={this.onDeactivateClick}>{isActive ? ('X Désactiver') : ('Activer')}</button>
              <NavLink  to={`${path}/${id}`} className="button is-secondary is-small">
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



export default connect(
  () => {
    const selectOccasionThumbUrl = createSelectOccasionThumbUrl()
    return (state, ownProps) => ({
      thumbUrl: selectOccasionThumbUrl(state, ownProps)
    })
  },
  { requestData }
)(OccasionItem)
