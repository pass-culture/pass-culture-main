import classnames from 'classnames'
import React, { Component } from 'react'
import Draggable from 'react-draggable'
import { Portal } from 'react-portal'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FavoriteItem from './FavoriteItem'
import withFrontendOffer from '../hocs/withFrontendOffer'
import { filterData, requestData } from '../reducers/data'

class Card extends Component {
  constructor () {
    super ()
    this.state = {
      dislikedOpacity: 0,
      interestingOpacity: 0,
      isDragging: false,
      isFavorite: false,
      position: null,
      type: null
    }
  }
  handlePinHighlight = props => {
    const { index, pin, selectedItem } = props
    if (pin && pin.type === 'interesting' && index === selectedItem) {
      this.setState({ interestingOpacity: 1, isFavorite: true })
    } else {
      this.setState({ interestingOpacity: 0, isFavorite: false })
    }
  }
  onContentClick = () => {
    const { history, id } = this.props
    history.push(`/offres/${id}`)
  }
  onDeleteClick = () => {
    const { id, requestData } = this.props
    //TODO: remove favorite status
    //requestData('DELETE', `pins/offerId:${id}`, {
    //  getOptimistState: (state, action) => {
    //    const offerIds = state.offers.map(offer => offer.id)
    //    const offerIndex = offerIds.indexOf(id)
    //    const optimistOffers = [...state.offers]
    //    optimistOffers[offerIndex] = Object.assign({}, optimistOffers[offerIndex])
    //    delete optimistOffers[offerIndex].pin
    //    return {
    //      offers: optimistOffers
    //    }
    //  },
    //  getSuccessState: (state, action) => {
    //    const offerIds = state.offers.map(({ id }) => id)
    //    const offerIndex = offerIds.indexOf(id)
    //    const nextOffers = [...state.offers]
    //    nextOffers[offerIndex] = Object.assign({}, nextOffers[offerIndex])
    //    delete nextOffers[offerIndex].pin
    //    return { offers: nextOffers }
    //  }
    //})
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
    const { isFavorite } = this.state
    const { y } = data
    let type
    if (y < -thresholdDragRatio * this._element.offsetHeight) {
      type = 'interesting'
    } else if (y > thresholdDragRatio * this._element.offsetHeight) {
      type = 'disliked'
    }
    if (type) {
      //TODO: mark item as favorite
      //requestData('POST', 'pins', { body: {
      //  offerId: id,
      //  type,
      //  userId
      //}})
      carousselElement.selectItem({ selectedItem: (index < itemsCount - 1)
        ? index
        : index -1
      })
      filterData('offers', offer => offer.id !== id)
      // nextButtonElement.click()
    }
    this.setState({
      dislikedOpacity: 0,
      interestingOpacity: isFavorite ? 1 : 0,
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
      venuesFavorites,
      thumbUrl
    } = this.props
    const { dislikedOpacity,
      interestingOpacity,
      isDisabled,
      isDragging,
      isFavorite,
      position
    } = this.state
    return (
      <div className='card flex items-center justify-center'
        ref={_element => this._element = _element}>
        {
          selectedItem === index && [
            <Portal key='interesting' node={carousselNode}>
              <div className={classnames('card__typed card__typed--interesting absolute p2 relative', {
                'card__typed--interesting--active': interestingOpacity >= 1 })}
                style={{ opacity: interestingOpacity }}>
                {
                  isFavorite && !isDragging && (
                    <button className='button button--alive button--reversed card__typed__delete absolute'
                      onClick={this.onDeleteClick}>
                      X
                    </button>
                  )
                }
                pourquoi pas
              </div>
            </Portal>,
            <Portal key='disliked' node={carousselNode}>
              <div className={classnames('card__typed card__typed--disliked absolute p2', {
                'card__typed--disliked--active': dislikedOpacity >= 1
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
          <div className='card__content relative' style={{
            backgroundImage: `url(${thumbUrl})`,
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover'
          }} onDoubleClick={this.onContentClick}>
            <div className='card__content__info absolute bottom-0 left-0 right-0 m2 p1 relative'>
              <div className='mb1'>
                à {(20-id)*15}m
              </div>
              <div className='flex items-center justify-center'>
              {
                venuesFavorites && venuesFavorites.map((venuesFavorite, index) =>
                  <FavoriteItem key={index} {...venuesFavorite} />
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

Card.defaultProps = {
  thresholdDragRatio: 0.3
}

export default compose(
  withRouter,
  withFrontendOffer,
  connect(
    state => ({ userId: state.user && state.user.id }),
    { filterData, requestData }
  )
)(Card)
