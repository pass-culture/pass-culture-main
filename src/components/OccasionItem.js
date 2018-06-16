import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Price from './Price'
import Icon from './layout/Icon'
import { requestData } from '../reducers/data'
import createSelectMediations from '../selectors/mediations'
import createSelectOccasionItem from '../selectors/occasionItem'
import createSelectOccasionThumbUrl from '../selectors/occasionThumbUrl'
import createSelectOccurences from '../selectors/occurences'
import {API_URL} from '../utils/config'
import { modelToPath } from '../utils/translate'
import { pluralize } from '../utils/string'

class OccasionItem extends Component {

  constructor () {
    super()
    this.state = {
      path: null
    }
  }

  onDeactivateClick = event => {
    const {
      occasion,
      occasionType,
      requestData
    } = this.props
    const {
      id,
      isActive
    } = (occasion || {})
    requestData(
      'PATCH',
      `occasions/${occasionType}/${id}`,
        {
          body: {
            occasion: {
              isActive: !isActive
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
      mediations,
      occasionItem,
      occasion,
      occurences,
      thumbUrl,
    } = this.props
    const {
      createdAt,
      description,
      id,
      isActive,
      name
    } = (occasion || {})
    const {
      available,
      maxDate,
      groupSizeMin,
      groupSizeMax,
      priceMin,
      priceMax,
    } = (occasionItem || {})
    const { path } = this.state
    const mediationsLength = get(mediations, 'length')
    return (
      <li className={classnames('occasion-item', { active: isActive })}>
        <img alt='thumbnail' src={thumbUrl} className="occasion-thumb"/>
        <div className="list-content">
          <NavLink className='name' to={`${path}/${id}`} title={name}>
            <Dotdotdot clamp={1}>{name}</Dotdotdot>
          </NavLink>
          <ul className='infos'>
            {moment(createdAt).isAfter(moment().add(-1, 'days')) && <li><div className='recently-added'></div></li>}
            <li className='is-uppercase'>Théâtre</li>
            <li className='has-text-primary'>{pluralize(get(occurences, 'length'), 'date')}</li>
            <li>{maxDate && `jusqu'au ${maxDate.format('DD/MM/YYYY')}`}</li>
            {groupSizeMin > 0 && <li>{groupSizeMin === groupSizeMax ? groupSizeMin : `entre ${groupSizeMin} et ${groupSizeMax} personnes`}</li>}
            {available > 0 && <li>restent {available}</li>}
            <li>{priceMin === priceMax ? <Price value={priceMin} /> : (<span><Price value={priceMin} /> - <Price value={priceMax} /></span>)}</li>
          </ul>
          <ul className='actions'>
            <li>
              <NavLink  to={`${path}/${id}${mediationsLength ? '' : '/accroches/nouveau'}`} className={`button is-small ${mediationsLength ? 'is-secondary' : 'is-primary is-outlined'}`}>
                <span className='icon'><Icon svg='ico-stars' /></span>
                <span>{get(mediations, 'length') ? 'Accroches' : 'Ajouter une Accroche'}</span>
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
    const selectMediations = createSelectMediations()
    const selectOccurences = createSelectOccurences()
    const selectOccasionItem = createSelectOccasionItem(selectOccurences)
    const selectOccasionThumbUrl = createSelectOccasionThumbUrl(selectMediations)
    return (state, ownProps) => ({
      mediations: selectMediations(state, ownProps),
      occasionItem: selectOccasionItem(state, ownProps),
      occurences: selectOccurences(state, ownProps),
      thumbUrl: selectOccasionThumbUrl(state, ownProps)
    })
  },
  { requestData }
)(OccasionItem)
