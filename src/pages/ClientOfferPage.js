import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from '../components/Icon'
import { requestData } from '../reducers/data'
import { URL } from '../utils/config'

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
            <h2>
              {offer.work.name}
              { offer.sellersFavorites && offer.sellersFavorites.length>0 && <Icon name='favorite-outline' /> }
              { offer.prices.filter(p => p.groupSize>1) && <Icon name='error' /> }
            </h2>
            <img className='offerPicture' src={ URL+'/thumbs/'+offer.work.id } />
            <h3>Offres</h3>
            <ul className="prices">
              { offer.prices.map(price => (
                                           <li>
                                              {price.value} €
                                              {price.groupSize > 1 && " si vous y allez avec "+(price.groupSize-1)+" amis !"}
                                           </li>
                                         )) }
            </ul>
          </div>
          )
        }
      </main>
    )
  }
}

export default connect((state, ownProps) => ({ offer: state.data['offers/'+ownProps.offerId] }),
                       { requestData })(ClientOfferPage)
