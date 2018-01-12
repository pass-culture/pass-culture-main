import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'

class ClientOfferPage extends Component {
  render = () => {
    return (
      <main className='page client-offer-page flex flex-column'>
        <h2>Le bourgeois Gentillhomme</h2>
      </main>
    )
  }
}

//export default connect((state, ownProps) => state.data.offers.filter(o => o.id===ownProps.params.offerId),
//                       { requestData })(ClientOfferPage)
export default ClientOfferPage
