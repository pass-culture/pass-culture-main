import moment from 'moment'
import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { connect } from 'react-redux'
import { Carousel } from 'react-responsive-carousel'
import { compose } from 'redux'

import Card from './Card'
import LoadingCard from './LoadingCard'
import SearchInput from '../components/SearchInput'
import { assignData, requestData } from '../reducers/data'
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
  handleRequestData = props => {
    const { userId, requestData } = this.props
    // if there is a user we gonnat get directly
    // in the dexie local db else we ask directly to
    // the backend
    requestData('GET',
      userId ? 'userMediations' : 'randomOffers',
      {
        hook: !userId && this.handleOfferToUserMediation,
        sync: userId
      }
    )
  }
  handleOfferToUserMediation = (method, path, result, config) => {
    const { assignData,
      userId,
      userMediations,
      requestData
    } = this.props
    if (!result.data) {
      return
    }
    if (!userId || (config.value && config.value.length > 0)) {
      let nextUserMediations = result.data.map(offer => ({
        isClicked: false,
        isFavorite: false,
        offer
      }))
      if (!userId) {
        nextUserMediations = (userMediations &&
          userMediations.concat(nextUserMediations)) ||
          nextUserMediations
      }
      assignData({ userMediations: nextUserMediations })
    } else if (userId) {
      requestData('PUT', 'userMediations', { sync: true })
    }
  }
  onChange = selectedItem => {
    const { requestData,
      userId,
      userMediations
    } = this.props
    const newState = { selectedItem }
    if (userId) {
      // update dateRead for previous item
      const { id, isFavorite } = userMediations[selectedItem - 1]
      const body = [{ dateRead: moment().toISOString(), id, isFavorite }]
      requestData('PUT', 'userMediations', { body, sync: true })
    } else if (selectedItem === userMediations.length - 1) {
      requestData('GET', 'randomOffers', { hook: this.handleOfferToUserMediation })
    }
    this.setState(newState)
  }
  componentWillMount () {
    this.handleRequestData()
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
    const { userId, userMediations } = nextProps
    if (this.carouselElement && userMediations !== this.props.userMediations) {
      this.handleLoading(nextProps)
      //this.carouselElement.selectItem({ selectedItem: 0 })
    }
    if (userId && userId !== this.props.userId) {
      this.handleRequestData()
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
            hook={this.handleOfferToUserMediation}
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
      loadingTag: state.loading.tag,
      userId: state.user && state.user.id,
      userMediations: state.data.userMediations
    }),
    { assignData, closeLoading, requestData, showLoading }
  )
)(Explorer)
