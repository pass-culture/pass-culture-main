import React, { Component } from 'react'
import Draggable from 'react-draggable'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import SellerFavoriteItem from './SellerFavoriteItem'
import { filterData, requestData } from '../reducers/data'
import { API_URL } from '../utils/config'

class OfferCard extends Component {
  constructor () {
    super ()
    this.state = { position: null }
  }
  onContentClick = () => {
    const { history, id } = this.props
    history.push(`/offres/${id}`)
  }
  onStart = () => {
    this.setState({ position: null })
  }
  onStop = (event, data) => {
    const { carousselElement,
      filterData,
      id,
      index,
      nextButtonElement,
      prevButtonElement,
      requestData,
      thresholdDragRatio,
      userId
    } = this.props
    const { y } = data
    let type
    if (y < -thresholdDragRatio * this._element.offsetHeight) {
      type = 'disliked'
    } else if (y > thresholdDragRatio * this._element.offsetHeight) {
      type = 'interesting'
    }
    if (type) {
      /*
      requestData('POST', 'pins', {
        offerId: id,
        type,
        userId
      })
      */
      filterData('offers', offer => offer.id !== id)
      this.props.carousselElement.selectItem({ selectedItem: index })
      // nextButtonElement.click()
      this.setState({ position: { x: 0, y: 0 } })
    } else {
      this.setState({ position: { x: 0, y: 0 } })
    }
  }
  render () {
    const { id,
      sellersFavorites,
      work
    } = this.props
    const { isDisabled, position } = this.state
    return (
      <div className='offer-card flex items-center justify-center'
        ref={_element => this._element = _element}>
        <Draggable axis='y'
          disabled={isDisabled}
          onDrag={this.onDrag}
          onStart={this.onStart}
          onStop={this.onStop}
          position={position} >
          <div className='offer-card__content relative' style={{
            backgroundImage: `url(${API_URL}/thumbs/${work.id})`,
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover'
          }} onClick={this.onContentClick}>
            <div className='offer-card__content__info absolute bottom-0 left-0 right-0 m2 p1'>
              à {(20-id)*15}m
              {
                sellersFavorites && sellersFavorites.map((sellersFavorite, index) =>
                  <SellerFavoriteItem key={index} {...sellersFavorite} />
                )
              }
            </div>
          </div>
        </Draggable>
      </div>
    )
  }
}

OfferCard.defaultProps = {
  thresholdDragRatio: 0.5
}

export default compose(
  withRouter,
  connect(
    state => ({ userId: state.user && state.user.id }),
    { filterData, requestData }
  )
)(OfferCard)
