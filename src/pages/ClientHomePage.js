import React, { Component } from 'react'

import OffersHorizScroller from '../components/OffersHorizScroller'
import SearchBar from '../components/SearchBar'

class ClientHomePage extends Component {
  render = () => {
    return (
      <main className='page client-home-page flex flex-column'>
        <OffersHorizScroller />
      </main>
    )
  }
}

export default ClientHomePage
