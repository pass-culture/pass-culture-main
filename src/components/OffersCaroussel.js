import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Carousel } from 'react-responsive-carousel'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import OfferCard from './OfferCard'
// import OfferSlide from './OfferSlide'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'

class OffersCaroussel extends Component {
  constructor () {
    super()
    this.state = { currentIndex: -1 }
  }
  handleCardClick = index => {
    const { history, modulo, offers } = this.props
    let offerId = offers[modulo + 3*index].id;
    history.push('/offres/' + offerId);
  }
  /*
  onChange = index => {
    const { filteredOffers, requestData, userId } = this.props
    if (index > this.state.currentIndex) {
        // it means user swiped to the left
        // which is the dislike gesture
        requestData('POST', 'pins', {
          offerId: filteredOffers[index].id,
          type: 'dislike',
          userId
        })
    }
    this.setState({ currentIndex: index })
  }
  */
  render () {
    const { filteredOffers, ItemComponent } = this.props
    return (
      <Carousel emulateTouch
        onClickItem={ index => this.handleCardClick(index) }
        showArrows={true}
        swipeScrollTolerance={2}
        showStatus={false}
        showIndicators={false}
        showThumbs={false}
        transitionTime={250} >
        {
          filteredOffers && filteredOffers.map((offer, index) =>
            <ItemComponent key={index} {...offer} />)
        }
      </Carousel>
    )
  }
}

OffersCaroussel.defaultProps = {
  ItemComponent: OfferCard
  // ItemComponent: OfferSlide
}

export default compose(
  withRouter,
  withSelectors({
    filteredOffers: [
      ownProps => ownProps.carousselsCount,
      ownProps => ownProps.modulo,
      ownProps => ownProps.offers,
      (carousselsCount, modulo, offers) =>
        offers.filter((offer, index) => index % carousselsCount === modulo )
    ]
  }),
  connect(
    state => ({ userId: state.user && state.user.id }),
    { requestData }
  )
)(OffersCaroussel)
