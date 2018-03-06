import React, { Component } from 'react'

class Card extends Component {
  render () {
    const { index, size } = this.props
    let style = {}
    if (index === 0) {
      style = { left: '-100%' }
    } else if (index < size + 1) {
      style = { left: `${index * 10}px` }
    } else if (index === size + 1) {
      style = { left: '100px', right: '100px' }
    } else if (index < 2 * size + 2) {
      style = { right: `${(2 * size + 2 - index) * 10}px` }
    } else {
      style = { right: '-100%' }
    }
  }
  onContentClick = () => {
    const { history, id, mediation } = this.props
    if (mediation) {
      history.push(`/decouverte/${id}/${mediation.id}`)
    }
    else {
      history.push(`/decouverte/${id}`)
    }
  }
  onDeleteClick = () => {
    // const { id, requestData } = this.props
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
    const { cardsCount,
      carouselElement,
      filterData,
      id,
      index,
      // requestData,
      thresholdDragRatio,
      // userId
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
      const selectedItem = (index < cardsCount - 1)
        ? index
        : index -1
      carouselElement.selectItem({ selectedItem })
      filterData('offers', offer => offer.id !== id)
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
    const { cardsLength,
      carousselNode,
      dateRead,
      id,
      index,
      isHidden,
      mediation,
      selectedItem,
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
      <div className='card absolute'
        style={style} >
        {index}
      </div>
    )
  }
}

export default Card
