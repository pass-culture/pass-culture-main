import moment from 'moment'
import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { connect } from 'react-redux'
import { Carousel } from 'react-responsive-carousel'
import { compose } from 'redux'

import Card from './Card'
import LoadingCard from './LoadingCard'
import SearchInput from '../components/SearchInput'
import withSelectors from '../hocs/withSelectors'
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
    const { user, requestData } = props
    // wait that we test already if there is a user
    if (user === null) {
      return
    }
    // if there is a user we gonna get directly
    // in the dexie local db
    // else if user is false we ask directly to the backend
    requestData('GET',
      user ? 'userMediations' : 'anonymousOffers',
      {
        hook: !user && this.handleOfferToUserMediation,
        sync: user
      }
    )
  }
  handleOfferToUserMediation = (method, path, result, config) => {
    const { assignData,
      user,
      userMediations,
      requestData
    } = this.props
    if (!result.data) {
      return
    }
    if (!user || (config.value && config.value.length > 0)) {
      let nextUserMediations = result.data.map(offer => ({
        isClicked: false,
        isFavorite: false,
        offer
      }))
      if (!user) {
        nextUserMediations = (userMediations &&
          userMediations.concat(nextUserMediations)) ||
          nextUserMediations
      }
      assignData({ userMediations: nextUserMediations })
    } else if (user) {
      requestData('PUT', 'userMediations', { sync: true })
    }
  }
  onChange = selectedItem => {
    const { hasFirstItem,
      requestData,
      user,
      userMediations
    } = this.props
    const newState = { selectedItem }
    const previousSelectedItem = selectedItem - 1
    if (user && selectedItem > (hasFirstItem ? 0 : 1) && previousSelectedItem === this.state.selectedItem) {
      // update dateRead for previous item
      const { dateRead, id, isFavorite } = userMediations[previousSelectedItem]
      // not update if already have one
      if (!dateRead) {
        const nowDate = moment().toISOString()
        const body = [{
          dateRead: nowDate,
          dateUpdated: nowDate,
          id,
          isFavorite
        }]
        requestData('PUT', 'userMediations', { body, sync: true })
      }
    } else if (!user && userMediations && selectedItem === userMediations.length - 1) {
      requestData('GET', 'anonymousOffers', { hook: this.handleOfferToUserMediation })
    }
    // Ask for older items
    if (!hasFirstItem && selectedItem === 0 && this.state.selectedItem === 1) {
      console.log('userMediations[0]', userMediations[0])
      const unreadOrChangedSince = (userMediations[0].momentDateRead || moment())
                                      .subtract(1, 'd')
                                      .toISOString()
      requestData('PUT',
        `userMediations?unreadOrChangedSince=${unreadOrChangedSince}`,
        { sync: true }
      )
    }
    // update selectedItem
    this.setState(newState)
  }
  componentWillMount () {
    this.handleRequestData(this.props)
    this.handleLoading(this.props)
  }
  componentDidMount () {
    const newState = {
      carouselElement: this.carouselElement,
      carousselNode: findDOMNode(this.carouselElement),
    }
    if (Object.keys(newState).length > 0) {
      this.setState(newState)
    }
  }
  componentWillReceiveProps (nextProps) {
    const { firstNotReadItem,
      hasFirstItem,
      user,
      userMediations
    } = nextProps
    if (this.carouselElement && userMediations !== this.props.userMediations) {
      this.handleLoading(nextProps)
    }
    if (user !== this.props.user) {
      this.handleRequestData(nextProps)
    }
    // get directly to the not read
    if (this.state.selectedItem === 0) {
      // shift
      console.log('hasFirstItem', hasFirstItem, firstNotReadItem)
      const selectedItem = (firstNotReadItem || 0) + (hasFirstItem ? 0 : 1)
      console.log('selectedItem', selectedItem)
      this.setState({ selectedItem })
    }
    if (user === false && this.props.user) {
      this.setState({ selectedItem: 1 })
    }
  }
  render () {
    const { loadingTag,
      user,
      userMediations
    } = this.props
    const { selectedItem } = this.state
    console.log('userMediations', userMediations)
    return (
      <div className='explorer mx-auto p2' id='explorer'>
        <div className='explorer__search absolute'>
          <SearchInput collectionName='offers'
            hook={this.handleOfferToUserMediation} />
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
              ? ((user && [<LoadingCard key='first' isForceActive />]) || []).concat(
                  userMediations.map((userMediation, index) =>
                    <Card {...this.state}
                      index={index}
                      itemsCount={userMediations.length}
                      key={index}
                      {...userMediation}
                      {...userMediation.mediation && userMediation.mediation.offer}
                      {...userMediation.offer} />
                  )).concat([<LoadingCard key='next' isForceActive />])
              : <LoadingCard />
          }
        </Carousel>
      </div>
    )
  }
}

function groupBy(list, keyGetter) {
    const map = new Map();
    list.forEach((item) => {
        const key = keyGetter(item);
        const collection = map.get(key);
        if (!collection) {
            map.set(key, [item]);
        } else {
            collection.push(item);
        }
    });
    return map;
}

export default compose(
  connect(
    (state, ownProps) => ({
      loadingTag: state.loading.tag,
      user: state.user,
      userMediations: state.data.userMediations
    }),
    { assignData, closeLoading, requestData, showLoading }
  ),
  withSelectors({
    userMediations: [
      ownProps => ownProps.userMediations,
      userMediations => {
        if (!userMediations) {
          return userMediations
        }
        // sort given dateRead
        const groupe = groupBy(userMediations,
          um => um.dateRead === null)
        let notReadUms = groupe.get(true)
        const firstNotRead = notReadUms && notReadUms.find(um => um.isFirst)
        if (firstNotRead) {
          notReadUms = [firstNotRead].concat(notReadUms)
        }
        let readUms = groupe.get(false)
        if (!readUms) {
          return notReadUms
        }
        readUms.forEach(readUm => readUm.momentDateRead = moment(readUm.dateRead))
        readUms.sort((um1, um2) => um1.momentDateRead - um2.momentDateRead)
        // filter too old date Read items (later than one day)
        const tooOldThresholDate = moment().subtract(1, 'd')
        const firstReadUmIndex = readUms && readUms
          .map((readUm, index) => [readUm.momentDateRead, index])
          .find(tuple => tuple[0] > tooOldThresholDate)[1]
        readUms = readUms.slice(firstReadUmIndex)
        // return read - not read items
        return notReadUms ? readUms.concat(notReadUms) : readUms
      }
    ],
    firstNotReadItem: [
      (ownProps, nextState) => nextState.userMediations,
      userMediations => userMediations && userMediations.map(um => um.dateRead)
                                                        .indexOf(null)
    ],
    hasFirstItem: [
      (ownProps, nextState) => nextState.userMediations,
      userMediations => userMediations && userMediations[0] && userMediations[0].isFirst
    ]
  }),
)(Explorer)
