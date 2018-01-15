import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Carousel } from 'react-responsive-carousel'

import Icon from '../components/Icon'
import { requestData } from '../reducers/data'


class OffersHorizScroller extends Component {
  componentWillMount = () => {
    const { requestData } = this.props;
    requestData('GET', `offers`)
  }

  handleCardClick = (modulo, cardIndex) => {
    let offerId = this.props.offers[modulo*3+cardIndex].id;
    this.props.history.push('/offres/'+offerId);
  }

  renderCarousel = (modulo) => {
    const { offers } = this.props;
    return (
        <Carousel showArrows={true} emulateTouch showStatus={false} showIndicators={false} showThumbs={false} onClickItem={ (cardIndex) => this.handleCardClick(modulo, cardIndex) }>
          {
            offers.filter((offer, index) => index % 3 === modulo )
                  .map((offer, index) =>
                  (
                      <div key={index}>
                        { offer.sellersFavorites && offer.sellersFavorites.length && <Icon name='favorite-outline' /> }
                        { offer.name }>
                        <img className='offerPicture' src={ offer.thumbnailUrl } />
                      </div>
                  ))
          }
        </Carousel>
      )
  }

  render = () => {
    const { offers } = this.props
    return (
      <div className='offer-horiz-scroller'>
        {
          offers ? [0,1,2].map(this.renderCarousel)
                 : <div className='no-offers'>Aucune offre à afficher</div>
        }
      </div>
    )
  }
}

export default compose(withRouter,
   connect(state => ({ offers: state.data.offers }), { requestData })
)(OffersHorizScroller)
