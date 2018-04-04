import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './Icon'
import ProfilePicture from './ProfilePicture'
import { requestData } from '../reducers/data'
import { closeModal } from '../reducers/modal'

class Menu extends Component {

  onDisableClick = event => {
    alert('Pas encore disponible')
    event.preventDefault()
  }

  onSignOutClick = () => {
    const { closeModal,
      requestData
    } = this.props
    requestData('GET', 'users/signout')
    closeModal()
  }

  render () {
    return (
      <div className='menu'>
        <div className='menu__header'>
          <div className='profile-pic'>
            <ProfilePicture className='avatar' />
            {this.props.user.publicName}
          </div>
          <div className='account'>
            <div>Mon Pass</div>
            <div><strong>——&nbsp;€</strong></div>
          </div>
        </div>
        <ul>
          <li>
            <NavLink to='/decouverte'>
              <Icon className='col-1' svg='ico-offres-w' />
              Les offres
            </NavLink>
          </li>
          <li>
            <NavLink to='/reservations'>
              <Icon className='col-1' svg='ico-calendar-w' />
              Mes réservations
            </NavLink>
          </li>
          <li className='disabled'>
            <NavLink to='/favoris'
              onClick={this.onDisableClick}>
              <Icon className='col-1' svg='ico-like-w' />
              Mes favoris
            </NavLink>
          </li>
          <li className='disabled'>
            <NavLink to='/reglages'
              onClick={this.onDisableClick}>
              <Icon className='col-1' svg='ico-settings-w' />
              Réglages
            </NavLink>
          </li>
          <li className='disabled'>
            <NavLink to='/profil'
              onClick={this.onDisableClick}>
              <Icon className='col-1' svg='ico-user-w' />
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

export default connect(
  state => ({ user: state.user }),
  { closeModal, requestData }
)(Menu)
