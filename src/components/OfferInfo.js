import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import ControlBar from './ControlBar'
import Icon from './Icon'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'
import { API_URL } from '../utils/config'

class OfferInfo extends Component {
  render = () => {
    const { bargainPrices,
      description,
      id,
      name,
      work,
      prices,
      sellersFavorites,
      sortedPrices
    } = this.props
    return (
      <div>
        <h2>
          { name || work.name }
          {
            sellersFavorites && sellersFavorites.length > 0 &&
            <Icon name='favorite-outline' />
          }
          { bargainPrices && bargainPrices.length > 1 && <Icon name='error' /> }
        </h2>
        <img alt='' className='offerPicture' src={`${API_URL}/thumbs/${work.id}`} />
        { description }
        <div className='clearfix' />
        <div className='sellerInfos'>
          <b>{ sortedPrices && sortedPrices[0].value }&nbsp;€</b><br/>
          { work.type==="book" ? "À la librairie" : "À 20h au théatre" } Tartenshmoll<br/>
          2 rue des Lilas (à {(20-id)*15}m)<br/>
          <img alt='' src='/map.png' /><br/>
          { work.type==='book' ? <span>Ouvert jusqu&apos;à 19h aujourd&quot;hui<br/><a href=''>voir tous les horaires</a></span>
                                    : <span><br/>Dates&nbsp;:<br/><img alt='' src='/calendrier.png' /><br/></span> }
        </div>

        { prices.length>1 &&
            (
            <div>
              <h3>Tarifs Pass Culture</h3>
              <ul className='prices'>
                {
                  prices.map(price => (
                     <li>
                        {price.value} €
                        {price.groupSize > 1 && ' si vous y allez avec '+(price.groupSize-1)+' amis !'}
                     </li>
                   ))
                }
              </ul>
            </div>
            )
        }
        <ControlBar offerId={id} />
      </div>
    )
  }
}

export default compose(
  connect(
    null,
    { requestData }
  ),
  withSelectors({
    bargainPrices: [
      ownProps => ownProps.prices,
      prices => prices.filter(p => p.groupSize>1)
    ],
    sortedPrices: [
      ownProps => ownProps.prices,
      prices => prices.sort((p1, p2) => p1.value > p2.value)
    ]
  })
)(OfferInfo)
