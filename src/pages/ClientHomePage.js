import React from 'react'

import OffersHorizScroller from '../components/OffersHorizScroller'
import withLogin from '../hocs/withLogin'

const ClientHomePage = () => {
  return (
    <main className='page client-home-page flex flex-column'>
      <OffersHorizScroller />
    </main>
  )
}

export default withLogin(ClientHomePage)
