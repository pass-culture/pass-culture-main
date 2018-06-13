import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import moment from 'moment'
import classnames from 'classnames'

// import FormInput from './layout/FormInput'
import Icon from './layout/Icon'
import { requestData } from '../reducers/data'
import createSelectOccasionThumbUrl from '../selectors/occasionThumbUrl'
import { modelToPath } from '../utils/translate'

import {API_URL} from '../utils/config'

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
              isActive: event.target.value
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
      name,
      thumbPath,
    } = this.props
    const {
      path
    } = this.state

    console.log(this.props)
    return (
      <li className={classnames('occasion-item', {active: isActive})}>
        <figure className='image is-96x96'>
          <img alt='thumbnail' src={`${API_URL}${thumbPath}`} className=""/>
        </figure>
        <div className="list-content">
          <NavLink className='name' to={`${path}/${id}`}>
            {name}
          </NavLink>
          <ul className='infos'>
            {moment(createdAt).isAfter(moment().add(-1, 'days')) && <li><div className='recently-added'></div></li>}
            <li className='is-uppercase'>Théâtre</li>
            <li className='has-text-primary'>3 dates</li>
            <li>jusqu'au 31/12/2018</li>
            <li>5</li>
            <li>5 écoulées</li>
            <li>restent 10</li>
            <li>5€</li>
          </ul>
          <ul className='actions'>
            <li>
              <NavLink  to={`${path}/${id}/accroches`} className="button is-primary is-small is-outlined">
                + Ajouter une Accroche
              </NavLink>
              <button className='button is-secondary' onClick={this.onDeactivateClick}>{isActive ? ('X Désactiver') : ('Activer')}</button>
            </li>
            <li>
              <NavLink  to={`${path}/${id}`} className="button is-secondary">
                <Icon svg='ico-pen-r' />
              </NavLink>
            </li>
          </ul>
          <nav className="level is-mobile">
            <div className="level-left">
            </div>
          </nav>
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
      // thumbUrl: selectOccasionThumbUrl(state, ownProps)
    })
  },
  { requestData }
)(OccasionItem)
