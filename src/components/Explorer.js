import moment from 'moment'
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
      selectedItem: 0
    }
  }
  handleLoading = props => {
    const { closeLoading, showLoading, userMediations } = props
    if (!userMediations || userMediations.length === 0) {
      showLoading()
      return
    }
    closeLoading()
  }
  handleSearchHook = (method, path, result, config) => {
    const { assignData, requestData } = this.props
    if (!result.data) {
      return
    }
    if (config.value &&  config.value.length > 0) {
      const userMediations = result.data.map(offer => ({
        isClicked: false,
        isFavorite: false,
        offer
      }))
      assignData({ userMediations })
    } else {
      requestData('PUT', 'userMediations', { sync: true })
    }
  }
  onChange = selectedItem => {
    const { requestData,
      userMediations
    } = this.props
    const newState = { selectedItem }
    // update dateRead for previous item
    const { id, isFavorite } = userMediations[selectedItem - 1]
    const body = [{ dateRead: moment().toISOString(), id, isFavorite }]
    requestData('PUT', 'userMediations', { body, sync: true })
    this.setState(newState)
  }
  componentWillMount () {
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
    const { userMediations } = nextProps
    if (this.carouselElement && userMediations !== this.props.userMediations) {
      this.handleLoading(nextProps)
      //this.carouselElement.selectItem({ selectedItem: 0 })
    }
  }
  render () {
    const { loadingTag,
      userMediations
    } = this.props
    const { selectedItem } = this.state
    return (
      <div className='explorer mx-auto p2' id='explorer'>
        <div className='explorer__search absolute'>
          <SearchInput collectionName='offers'
            hook={this.handleSearchHook}
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
            loadingTag !== 'search' && userMediations && userMediations.length > 0
              ? userMediations.map((userMediation, index) =>
                  <Card {...this.state}
                    index={index}
                    itemsCount={userMediations.length}
                    key={index}
                    {...userMediation}
                    {...userMediation.mediation && userMediation.mediation.offer}
                    {...userMediation.offer} />
                ).concat([<LoadingCard key='last' isForceActive />])
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
      userMediations: state.data.userMediations,
      loadingTag: state.loading.tag
    }),
    { closeLoading, requestData, showLoading }
  )
)(Explorer)
