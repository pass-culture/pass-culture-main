import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Carousel } from 'react-responsive-carousel'
import { compose } from 'redux'

import OfferCard from './OfferCard'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'

class OffersCaroussel extends Component {
  constructor () {
    super()
    this.state = { carousselElement: null }
  }
  componentDidMount () {
    const newState = { carousselElement: this.carousselElement }
    /*
    if (!this.state.nextButtonElement) {
      newState.nextButtonElement = document.querySelector('button.control-arrow.control-next')
    }
    if (!this.state.prevButtonElement) {
      newState.prevButtonElement = document.querySelector('button.control-arrow.control-prev')
    }
    */
    if (Object.keys(newState).length > 0) {
      this.setState(newState)
    }
  }
  render () {
    const { filteredOffers } = this.props
    const { carousselElement,
      nextButtonElement,
      prevButtonElement
    } = this.state
    return (
      <Carousel axis='horizontal'
        emulateTouch
        ref={_element => this.carousselElement = _element}
        showArrows={true}
        swipeScrollTolerance={100}
        showStatus={false}
        showIndicators={false}
        showThumbs={false}
        transitionTime={250} >
        {
          filteredOffers && filteredOffers.map((offer, index) =>
            <OfferCard carousselElement={carousselElement}
              index={index}
              nextButtonElement={nextButtonElement}
              prevButtonElement={prevButtonElement}
              key={index} {...offer} />
          )
        }
      </Carousel>
    )
  }
}

export default compose(
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
