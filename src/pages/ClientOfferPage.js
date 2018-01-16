import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from '../components/Icon'
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
          <div>
            <h2>{offer.work.name}</h2>
            <img className='offerPicture' src={ URL+'/thumbs/'+offer.work.id } />
            { offer.sellersFavorites && offer.sellersFavorites.length>0 && <Icon name='favorite-outline' /> }
          </div>
          )
        }
      </main>
    )
  }
}

export default connect((state, ownProps) => ({ offer: state.data['offers/'+ownProps.offerId] }),
                       { requestData })(ClientOfferPage)
