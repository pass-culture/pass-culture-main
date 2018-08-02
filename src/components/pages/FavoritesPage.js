import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import BookingItem from '../BookingItem'
import Main from '../layout/Main'

class FavoritesPage extends Component {
  render() {
    const { favorites } = this.props
    return (
      <Main name="favorites" redBg footer={{ borderTop: true }} backButton>
        <header>
          <h1>
Mes favoris
          </h1>
        </header>
        {favorites.length > 0 && (
          <div>
            <ul className="favorites">
              {favorites.map((b, index) => (
                <BookingItem key={index} {...b} />
              ))}
            </ul>
          </div>
        )}
        {favorites.length === 0 && (
          <div>
            <p className="nothing">
Pas encore de favoris.
            </p>
            <p className="nothing">
              <Link to="/decouverte" className="button is-primary">
                Allez-y !
              </Link>
            </p>
          </div>
        )}
      </Main>
    )
  }
}

export default connect(
  state => ({
    favorites: state.data.favorites || [],
  }),
  { requestData }
)(FavoritesPage)
