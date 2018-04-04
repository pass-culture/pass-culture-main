import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import TimeAgo from 'react-timeago'
import frenchStrings from 'react-timeago/lib/language-strings/fr-short'
import buildFormatter from 'react-timeago/lib/formatters/buildFormatter'

import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'
import MenuButton from '../components/layout/MenuButton'
import Icon from '../components/Icon'

const formatter = buildFormatter(Object.assign(frenchStrings, {
  prefixAgo: 'Il y a',
  prefixFromNow: 'Dans',
}))

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
                      <TimeAgo date={b.date} formatter={formatter} />
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
        date: new Date('04-30-2018'),
        token: 'A684P6',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'BM',
        name: 'Visite diurne',
        date: new Date('05-03-2018'),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'CM',
        name: 'Visite diurne',
        date: new Date('05-06-2018'),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'DM',
        name: 'Visite diurne',
        date: new Date('05-09-2018'),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'EM',
        name: 'Visite diurne',
        date: new Date('05-11-2018'),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'FM',
        name: 'Visite diurne',
        date: new Date('05-23-2018'),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'GM',
        name: 'Visite diurne',
        date: new Date('05-29-2018'),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }, {
        id: 'HM',
        name: 'Visite diurne',
        date: new Date('05-30-2018'),
        token: 'VF8996',
        thumbUrl: '/default_thumb.png',
        path: '/decouverte/AFUA/AM',
      }]
    }),
    { requestData }
  )
)(BookingsPage)
