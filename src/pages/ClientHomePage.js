import React from 'react'

import OffersHorizScroller from '../components/OffersHorizScroller'
// import OffersSwipe from '../components/OffersSwipe'
import withLogin from '../hocs/withLogin'

const ClientHomePage = ({ OffersComponent }) => {
  return (
    <main className='page client-home-page flex flex-column'>
      <OffersComponent />
    </main>
  )
}

ClientHomePage.defaultProps = {
  OffersComponent: OffersHorizScroller
}

export default withLogin(ClientHomePage)
