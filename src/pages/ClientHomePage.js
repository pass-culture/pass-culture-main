import React, { Component } from 'react'
import { connect } from 'react-redux'

import OffersHorizScroller from '../components/OffersHorizScroller'
import SearchBar from '../components/SearchBar'

class ClientHomePage extends Component {
  render = () => {
    return (
      <main className='page flex flex-column'>
        <SearchBar />
        <h3>Livres</h3>
        <OffersHorizScroller type='book' />
        <h3>Spectacle vivant</h3>
        <OffersHorizScroller type='theater' />
      </main>
    )
  }
}

export default ClientHomePage
