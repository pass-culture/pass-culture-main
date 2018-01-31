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
      isDragging: false,
      isPinned: false,
      position: null,
      type: null
    }
  }
  handlePinHighlight = props => {
    const { index, pin, selectedItem } = props
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
  onDeleteClick = () => {
    const { id, requestData } = this.props
    requestData('DELETE', `pins/offerId:${id}`, {
      getOptimistState: (state, action) => {
        const offerIds = state.offers.map(offer => offer.id)
        const offerIndex = offerIds.indexOf(id)
        const optimistOffers = [...state.offers]
        optimistOffers[offerIndex] = Object.assign({}, optimistOffers[offerIndex])
        delete optimistOffers[offerIndex].pin
        return {
          offers: optimistOffers
        }
      },
      getSuccessState: (state, action) => {
        const offerIds = state.offers.map(({ id }) => id)
        const offerIndex = offerIds.indexOf(id)
        const nextOffers = [...state.offers]
        nextOffers[offerIndex] = Object.assign({}, nextOffers[offerIndex])
        delete nextOffers[offerIndex].pin
        return { offers: nextOffers }
      }
    })
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
    this.setState({ position: null, isDragging: true })
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
      thresholdDragRatio,
      userId
    } = this.props
    const { isPinned } = this.state
    const { y } = data
    let type
    if (y < -thresholdDragRatio * this._element.offsetHeight) {
      type = 'interesting'
    } else if (y > thresholdDragRatio * this._element.offsetHeight) {
      type = 'disliked'
    }
    if (type) {
      requestData('POST', 'pins', { body: {
        offerId: id,
        type,
        userId
      }})
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
      isDragging: false,
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
    const { carousselNode,
      id,
      index,
      selectedItem,
      sellersFavorites,
      hasThumb
    } = this.props
    const workOrEvent = this.props.work || this.props.event
    const { dislikedOpacity,
      interestingOpacity,
      isDisabled,
      isDragging,
      isPinned,
      position
    } = this.state
    return (
      <div className='offer-card flex items-center justify-center'
        ref={_element => this._element = _element}>
        {
          selectedItem === index && [
            <Portal key='interesting' node={carousselNode}>
              <div className={classnames('offer-card__typed offer-card__typed--interesting absolute p2 relative', {
                'offer-card__typed--interesting--active': interestingOpacity >= 1 })}
                style={{ opacity: interestingOpacity }}>
                {
                  isPinned && !isDragging && (
                    <button className='button button--alive button--reversed offer-card__typed__delete absolute'
                      onClick={this.onDeleteClick}>
                      X
                    </button>
                  )
                }
                pourquoi pas
              </div>
            </Portal>,
            <Portal key='disliked' node={carousselNode}>
              <div className={classnames('offer-card__typed offer-card__typed--disliked absolute p2', {
                'offer-card__typed--disliked--active': dislikedOpacity >= 1
              })}
                style={{ opacity: dislikedOpacity }} >
                pas pour moi
              </div>
            </Portal>
          ]
        }
        <Draggable axis='y'
          disabled={isDisabled}
          onDrag={this.onDrag}
          onStart={this.onStart}
          onStop={this.onStop}
          position={position} >
          <div className='offer-card__content relative' style={{
            backgroundImage: `url(${API_URL}/thumbs/${hasThumb ? id : workOrEvent.id})`,
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover'
          }} onDoubleClick={this.onContentClick}>
            <div className='offer-card__content__info absolute bottom-0 left-0 right-0 m2 p1 relative'>
              <div className='mb1'>
                à {(20-id)*15}m
              </div>
              <div className='flex items-center justify-center'>
              {
                sellersFavorites && sellersFavorites.map((sellersFavorite, index) =>
                  <SellerFavoriteItem key={index} {...sellersFavorite} />
                )
              }
              </div>
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
