import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { connect } from 'react-redux'
import { Carousel } from 'react-responsive-carousel'
import { compose } from 'redux'

import Card from './Card'
import LoadingCard from './LoadingCard'
import SearchInput from '../components/SearchInput'
import { requestData } from '../reducers/data'
import { closeLoading, showLoading } from '../reducers/loading'

class Explorer extends Component {
  constructor () {
    super()
    this.state = { carouselElement: null,
      carousselNode: null,
      hasRequested: false,
      selectedItem: 0
    }
  }
  handleLoading = props => {
    const { closeLoading, elements, showLoading } = props
    if (!elements || elements.length === 0) {
      showLoading()
      return
    }
    closeLoading()
  }
  handleRequestData = props => {
    const { collectionName, requestData, userId } = props
    userId && requestData('GET',
      collectionName,
      { isGeolocated: true, sync: true }
    )
  }
  onChange = selectedItem => {
    /*
    const { collectionName, elements, requestData } = this.props
    const { hasRequested } = this.state
    const newState = { selectedItem }
    if (elements && !hasRequested && selectedItem === elements.length - 1) {
      requestData('POST', collectionName)
      newState.hasRequested = true
    } else if (selectedItem === 0) {
      newState.hasRequested = false
    }
    this.setState(newState)
    */
  }
  componentWillMount () {
    this.handleRequestData(this.props)
    this.handleLoading(this.props)
  }
  componentDidMount () {
    const newState = {
      carouselElement: this.carouselElement,
      carousselNode: findDOMNode(this.carouselElement),
      // searchElement: this.searchElement,
      // searchNode: findDOMNode(this.searchElement)
    }
    if (Object.keys(newState).length > 0) {
      this.setState(newState)
    }
  }
  componentWillReceiveProps (nextProps) {
    const { elements, userId } = nextProps
    if (userId && (!this.props.userId || userId !== this.props.userId)) {
      this.handleRequestData(nextProps)
    }
    if (this.carouselElement && elements !== this.props.elements) {
      this.handleLoading(nextProps)
      //this.carouselElement.selectItem({ selectedItem: 0 })
    }
  }
  render () {
    const { collectionName,
      elements,
      isLoadingActive,
      searchCollectionName,
      searchHook
    } = this.props
    const { selectedItem } = this.state
    return (
      <div className='explorer mx-auto p2' id='explorer'>
        <div className='explorer__search absolute'>
          <SearchInput collectionName={searchCollectionName || collectionName}
            hook={searchHook}
            ref={element => this.searchElement = element} />
        </div>
        <Carousel axis='horizontal'
          emulateTouch
          ref={element => this.carouselElement = element}
          selectedItem={selectedItem}
          showArrows={true}
          swipeScrollTolerance={100}
          showStatus={false}
          showIndicators={false}
          showThumbs={false}
          transitionTime={250}
          onChange={this.onChange} >
          {
            !isLoadingActive && elements && elements.length > 0
              ? elements.map((element, index) =>
                  <Card {...this.state}
                    index={index}
                    itemsCount={elements.length}
                    key={index}
                    {...element}
                    {...element.mediation && element.mediation.offer}
                    {...element.offer} />
                )
              : <LoadingCard />
          }
        </Carousel>
      </div>
    )
  }
}

export default compose(
  connect(
    (state, ownProps) => ({
      elements: state.data[ownProps.collectionName],
      isLoadingActive: state.loading.isActive,
      userId: state.user && state.user.id
    }),
    { closeLoading, requestData, showLoading }
  )
)(Explorer)
