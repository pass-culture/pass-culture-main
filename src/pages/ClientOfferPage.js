import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'

class ClientOfferPage extends Component {
  componentWillMount = () => {
    const { requestData, offerId } = this.props;
    requestData('GET', 'offers/' + offerId)
  }

  render = () => {
    const { offer } = this.props;
    return (
      <main className='page client-offer-page flex flex-column'>
        {
        offer &&
          (
          <h2>{offer.name}</h2>
          )
        }
      </main>
    )
  }
}

export default connect((state, ownProps) => ({ offer: state.data['offers/'+ownProps.offerId] }),
                       { requestData })(ClientOfferPage)
