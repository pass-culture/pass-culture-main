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
              { offer.name || offer.work.name }
              { offer.sellersFavorites && offer.sellersFavorites.length>0 && <Icon name='favorite-outline' /> }
              { offer.prices.filter(p => p.groupSize>1) && <Icon name='error' /> }
            </h2>
            <img alt='' className='offerPicture' src={ URL+'/thumbs/'+offer.work.id } />
            { offer.description }
            <div className='clearfix' />
            <div className='sellerInfos'>
              <b>{ offer.prices.sort((p1, p2) => p1.value > p2.value)[0].value }&nbsp;€</b><br/>
              { offer.work.type=="book" ? "À la librairie" : "À 20h au théatre" } Tartenshmoll<br/>
              2 rue des Lilas (à {offer.id*25}m)<br/>
              <img alt='' src='/map.png' /><br/>
              { offer.work.type=="book" ? <span>Ouvert jusqu&quot;à 19h aujourd&quot;hui<br/></span>
                                        : <span><br/>Dates&nbsp;:<br/><img alt='' src='/calendrier.png' /><br/></span> }
              <a href=''>voir tous les horaires</a>
            </div>

            { offer.prices.length>1 &&
                (
                <div>
                  <h3>Tarifs Pass Culture</h3>
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
          </div>
          )
        }
      </main>
    )
  }
}

export default connect(
  (state, ownProps) => ({ offer: state.data['offers/'+ownProps.offerId] }),
  { requestData }
)(ClientOfferPage)
