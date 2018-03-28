import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Icon from './Icon'
import { requestData } from '../reducers/data'

class Menu extends Component {

  onSignOutClick = () => {
    this.props.requestData('GET', 'users/signout')
  }

  render () {
    return (
      <div className='menu'>
        <div className='menu__header'>
          <div className='profile-pic'>
            <img src='/icons/ico-user-w@2x.png' alt='avatar' className='avatar' />
            {this.props.user.publicName}
          </div>
          <div className='account'>
            <div>Mon Pass</div>
            <div><strong>0€</strong></div>
          </div>
        </div>
        <ul>
          <li>
            <NavLink to='/decouverte'>
              <Icon svg='ico-offres-w' />
              Toutes les offres
            </NavLink>
          </li>
          <li>
            <NavLink to='/reservations'>
              <Icon svg='ico-calendar-w' />
              Mes réservations
            </NavLink>
          </li>
          <li>
            <NavLink to='/favorites'>
              <Icon svg='ico-like-w' />
              Mes favoris
            </NavLink>
          </li>
          <li>
            <NavLink to='/reglages'>
              <Icon svg='ico-settings-w' />
              Réglages
            </NavLink>
          </li>
          <li>
            <NavLink to='/profil'>
              <Icon svg='ico-user-w' />
              Mon profil
            </NavLink>
          </li>
        </ul>
        <div className='stick-to-bottom'>
          <button onClick={this.onSignOutClick}>
            <Icon svg='ico-deconnect-w' />
            Déconnexion
          </button>
        </div>
      </div>
    )
  }
}

export default compose(
  // // withRouter is necessary to  make update the component
  // // given a location path change
  // withRouter,
  connect(
    state => ({
      user: state.user
    }), {
      requestData
    }
  )
)(Menu)
