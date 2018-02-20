import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { connect } from 'react-redux'
import { Carousel } from 'react-responsive-carousel'
import { compose } from 'redux'

import OfferCard from './OfferCard'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'

class OffersCaroussel extends Component {
  constructor () {
    super()
    this.state = { carousselElement: null,
      carousselNode: null,
      hasUserMediationRequested: false,
      selectedItem: 0
    }
  }
  componentDidMount () {
    const newState = {
      carousselElement: this.carousselElement,
      carousselNode: findDOMNode(this.carousselElement)
    }
    if (Object.keys(newState).length > 0) {
      this.setState(newState)
    }
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.filteredOffers !== this.props.filteredOffers) {
      this.carousselElement.selectItem({ selectedItem: 0 })
    }
  }
  onChange = selectedItem => {
    const { filteredOffers, requestData } = this.props
    const { hasUserMediationRequested } = this.state
    const newState = { selectedItem }
    if (!hasUserMediationRequested && selectedItem === filteredOffers.length - 1) {
      requestData('POST', 'user_mediations')
      newState.hasUserMediationRequested = true
    } else if (selectedItem === 0) {
      newState.hasUserMediationRequested = false
    }
    this.setState(newState)
  }
  render () {
    const { filteredOffers } = this.props
    const { selectedItem } = this.state
    return (
      <Carousel axis='horizontal'
        emulateTouch
        ref={_element => this.carousselElement = _element}
        selectedItem={selectedItem}
        showArrows={true}
        swipeScrollTolerance={100}
        showStatus={false}
        showIndicators={false}
        showThumbs={false}
        transitionTime={250}
        onChange={this.onChange} >
        {
          filteredOffers && filteredOffers.map((offer, index) =>
            <OfferCard {...this.state}
              index={index}
              itemsCount={filteredOffers.length}
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
