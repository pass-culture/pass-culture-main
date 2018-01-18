import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Carousel } from 'react-responsive-carousel'

import Icon from '../components/Icon'
import { requestData } from '../reducers/data'
import { API_URL } from '../utils/config'


class OffersHorizScroller extends Component {
  componentWillMount = () => {
    const { requestData } = this.props;
    requestData('GET', `offers?hasPrice=true`)
  }

  handleCardClick = (modulo, cardIndex) => {
    let offerId = this.props.offers[modulo+3*cardIndex].id;
    this.props.history.push('/offres/'+offerId);
  }

  renderCarousel = (modulo) => {
    const { offers } = this.props;
    return (
        <Carousel key={'carousel'+modulo}
                  emulateTouch
                  onClickItem={ (cardIndex) => this.handleCardClick(modulo, cardIndex) }
                  showArrows={true}
                  swipeScrollTolerance={2}
                  showStatus={false}
                  showIndicators={false}
                  showThumbs={false}
                  transitionTime={250} >
          {
            offers.filter((offer, index) => index % 3 === modulo )
                  .map((offer, index) =>
                  (
                      <div key={'slide'+modulo+3*index}>
                        <img alt='' className='offerPicture' src={ API_URL+'/thumbs/'+offer.work.id } />
                        { offer.sellersFavorites && offer.sellersFavorites.length>0 && <Icon name='favorite-outline' /> }
                        { offer.prices.filter(p => p.groupSize>1).length>0 && <Icon name='error' /> }
                        { offer.prices.sort((p1, p2) => p1.value > p2.value)[0].value }&nbsp;€&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; à {offer.id*25}m
                        <div className='offerName'>{ offer.name || offer.work.name }</div>
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
          offers && offers.length>0 ? [0,1,2].map(this.renderCarousel)
                                    : <div className='no-offers'>Aucune offre à afficher</div>
        }
      </div>
    )
  }
}

export default compose(withRouter,
   connect(state => ({ offers: state.data.offers }), { requestData })
)(OffersHorizScroller)
