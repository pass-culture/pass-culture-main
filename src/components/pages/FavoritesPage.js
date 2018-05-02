import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import BookingItem from '../BookingItem'
import PageWrapper from '../layout/PageWrapper'
import withLogin from '../hocs/withLogin'
import { requestData } from '../../reducers/data'

class FavoritesPage extends Component {
  componentDidMount() {
    this.handleRequestBookings()
  }

  handleRequestBookings = () => {
    // TODO
    // this.props.requestData('GET', 'bookings', { local: true })
  }

  render() {
    const { favorites } = this.props
    return (
      <PageWrapper
        name="favorites"
        redBg
        menuButton={{ borderTop: true }}
        backButton
      >
        <header>Mes favoris</header>
        {favorites.length > 0 && (
          <div>
            <ul className="favorites">
              {favorites.map((b, index) => <BookingItem key={index} {...b} />)}
            </ul>
          </div>
        )}
        {favorites.length === 0 && (
          <div>
            <p className="nothing">Pas encore de favoris.</p>
            <p className="nothing">
              <Link to="/decouverte" className="button is-primary">
                Allez-y !
              </Link>
            </p>
          </div>
        )}
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    state => ({
      favorites: state.data.favorites || [],
    }),
    { requestData }
  )
)(FavoritesPage)
