import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Carousel } from 'react-responsive-carousel'

import Icon from '../components/Icon'
import { requestData } from '../reducers/request'


class OffersHorizScroller extends Component {
  componentWillMount = () => {
    const { requestData } = this.props;
    requestData('GET', `offers`)
  }

  handleCardClick = (offerId) => {
    this.props.history.push('/offres/'+offerId);
  }

  renderCarousel = (modulo) => {
    const { offers } = this.props;
    return (
        <Carousel showArrows={true} emulateTouch infiniteLoop showStatus={false} showIndicators={false} showThumbs={false}>
          {
            offers.filter((offer, index) => index % 3 === modulo )
                  .map((offer, index) =>
                  (
                      <div key={index} onClick={() => this.handleCardClick(offer.id)}>
                        { offer.sellersFavorites && offer.sellersFavorites.length && <Icon name='favorite-outline' /> }
                        { offer.name }>
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
                       connect((state, ownProps) => ( { offers: state.request.offers } ),
                               { requestData })
                      )(OffersHorizScroller)
