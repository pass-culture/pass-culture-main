import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'
import MenuButton from '../components/layout/MenuButton'
import Icon from '../components/Icon'

class BookingsPage extends Component {
  formatDate(date) {
    return 'Dans un mois'
  }

  render() {
    return (
      <div className='page bookings-page'>
        <header>Mes réservations</header>
        <div className='content'>
          <h4>Réservations</h4>
          <ul className='bookings'>
            {this.props.bookings.map(b => (
              <li key={b.id}>
                <Link to={b.path}>
                  <div className='thumb'>
                    <img src={b.thumbUrl} alt='Thumb' />
                  </div>
                  <div className='infos'>
                    <div className='top'>
                      <h5>{b.name}</h5>
                      <time dateTime={b.date}>{this.formatDate(b.date)}</time>
                    </div>
                    <div className='token'>{b.token}</div>
                  </div>
                  <div className='arrow'>
                    <Icon svg='ico-next-S' />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <MenuButton borderTop />
      </div>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      bookings: [{
        id: 'AM',
        name: 'Visite nocturne',
        date: new Date(),
        token: 'A684P6',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'BM',
        name: 'Visite diurne',
        date: new Date(),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'CM',
        name: 'Visite diurne',
        date: new Date(),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'DM',
        name: 'Visite diurne',
        date: new Date(),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'EM',
        name: 'Visite diurne',
        date: new Date(),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'FM',
        name: 'Visite diurne',
        date: new Date(),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'GM',
        name: 'Visite diurne',
        date: new Date(),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'HM',
        name: 'Visite diurne',
        date: new Date(),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }]
    }),
    { requestData }
  )
)(BookingsPage)
