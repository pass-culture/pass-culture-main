import classnames from 'classnames'
import React, { Component } from 'react'
import Draggable from 'react-draggable'
import { Portal } from 'react-portal'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import SellerFavoriteItem from './SellerFavoriteItem'
import { filterData, requestData } from '../reducers/data'
import { API_URL } from '../utils/config'

class OfferCard extends Component {
  constructor () {
    super ()
    this.state = {
      dislikedOpacity: 0,
      interestingOpacity: 0,
      isPinned: false,
      position: null,
      type: null
    }
  }
  handlePinHighlight = props => {
    const { index, pin, selectedItem } = props
    const { interestingOpacity } = this.state
    if (pin && pin.type === 'interesting' && index === selectedItem) {
      this.setState({ interestingOpacity: 1, isPinned: true })
    } else {
      this.setState({ interestingOpacity: 0, isPinned: false })
    }
  }
  onContentClick = () => {
    const { history, id } = this.props
    history.push(`/offres/${id}`)
  }
  onDrag = (event, data) => {
    const { thresholdDragRatio } = this.props
    const { y } = data
    const ratio = -y / (thresholdDragRatio * this._element.offsetHeight)
    this.setState({
      dislikedOpacity: Math.max(0, -ratio),
      interestingOpacity: Math.max(0, ratio)
    })
  }
  onStart = () => {
    this.setState({ position: null })
  }
  onStop = (event, data) => {
    const { carousselElement,
      filterData,
      id,
      index,
      itemsCount,
      // nextButtonElement,
      // prevButtonElement,
      requestData,
      selectedItem,
      thresholdDragRatio,
      userId
    } = this.props
    const { isPinned } = this.state
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
      carousselElement.selectItem({ selectedItem: (index < itemsCount - 1)
        ? index
        : index -1
      })
      filterData('offers', offer => offer.id !== id)
      // nextButtonElement.click()
    }
    this.setState({
      dislikedOpacity: 0,
      interestingOpacity: isPinned ? 1 : 0,
      position: { x: 0, y: 0 }
    })
  }
  componentDidMount () {
    this.handlePinHighlight(this.props)
  }
  componentWillReceiveProps (nextProps) {
    this.handlePinHighlight(nextProps)
  }
  render () {
    const { carousselElement,
      carousselNode,
      id,
      sellersFavorites,
      work
    } = this.props
    const { dislikedOpacity,
      interestingOpacity,
      isDisabled,
      position
    } = this.state
    return (
      <div className='offer-card flex items-center justify-center'
        ref={_element => this._element = _element}>
        <Portal node={carousselNode}>
          <div className={classnames('offer-card__interesting absolute p2', {
            'offer-card__interesting--active': interestingOpacity >= 1 })}
            style={{ opacity: interestingOpacity }}>
            pourquoi pas
          </div>
        </Portal>
        <Portal node={carousselNode}>
          <div className={classnames('offer-card__disliked absolute p2', {
            'offer-card__disliked--active': dislikedOpacity >= 1
          })}
            style={{ opacity: dislikedOpacity }} >
            pas pour moi
          </div>
        </Portal>
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
          }} onDoubleClick={this.onContentClick}>
            <div className='offer-card__content__info absolute bottom-0 left-0 right-0 m2 p1 relative'>
              <div className='mb1'>
                à {(20-id)*15}m
              </div>
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
  thresholdDragRatio: 0.3
}

export default compose(
  withRouter,
  connect(
    state => ({ userId: state.user && state.user.id }),
    { filterData, requestData }
  )
)(OfferCard)
