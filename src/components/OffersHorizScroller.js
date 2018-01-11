import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { createSelector } from 'reselect'
import { withRouter } from 'react-router'

import Icon from '../components/Icon'
import { requestData } from '../reducers/request'


class OffersHorizScroller extends Component {
  componentWillMount = () => {
    const { requestData, type } = this.props;
    requestData('GET', `offers?type=${type}`)
  }

  componentWillReceiveProps = (nextProps) => {
    if (nextProps.offers !== this.props.offers && this.isFetching) {
      this.isFetching = false;
      }
  }

  handleCardClick = (offerId) => {
    this.props.history.push('/offres/'+offerId);
  }

  handleScroll = (event) => {
    if (this.isFetching) {
      return
    }
    const { requestData, offers, type } = this.props;
    let scrollLeft = event.target.scrollLeft,
        cardWidth = this.viewPortElement.firstChild.offsetWidth,
        nCardsBeforeViewPort = scrollLeft / cardWidth,
        nCardsAfterViewPort = offers.length - ((this.viewPortElement.offsetWidth + scrollLeft) / cardWidth);
        console.log(nCardsAfterViewPort);
        if (nCardsAfterViewPort<10) {
          this.isFetching = true;
          requestData('GET', `offers?type=${type}&after=${offers.slice(-1)[0].id}&count=40`)
          }
  }
  
  render = () => {
    const { offers } = this.props
    return (
      <div className='offer-horiz-scroller flex overflow-auto' onScroll={this.handleScroll} ref={ element => { this.viewPortElement = element } }>
        { 
          offers ? offers.map((offer, index) =>
                     (
                       <div className='offer-card' key={index} onClick={() => this.handleCardClick(offer.id)}>
                         { offer.sellersFavorites && offer.sellersFavorites.length && <Icon name='favorite-outline' /> }
                         { offer.name }
                       </div>
                     ))
                 : <div className='no-offers'>Aucune offre à afficher</div>
        }
      </div>
    )
  }
}

export default compose(withRouter,
                       connect(createSelector(state => state.request.offers,
                                              (state, ownProps) => ownProps.type,
                                              (offers, type) => ({ offers: offers && offers.filter(o => o.work.category === type) })),
                              { requestData })
                      )(OffersHorizScroller)
