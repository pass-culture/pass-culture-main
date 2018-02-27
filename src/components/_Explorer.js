import moment from 'moment'
import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { connect } from 'react-redux'
import { Carousel } from 'react-responsive-carousel'
import { compose } from 'redux'

import Card from './Card'
import LastCard from './LastCard'
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
      forcedItem: null,
      lastItem: false,
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
  handleRequestPrevious = props => {
    const { hasFirstItem, userMediations } = props
    if (userMediations &&
      this.props.userMediations &&
      this.props.userMediations.length < userMediations.length &&
      this.props.userMediations[0]
    ) {
      let forcedItem = userMediations &&
        userMediations.indexOf(this.props.userMediations[0])
      if (forcedItem > 0) {
        if (!hasFirstItem) {
          forcedItem = forcedItem - 1
        }
        this.setState({ forcedItem })
        return
      }
    }
  }
  handleRequestData = props => {
    const { assignData, user, requestData } = props
    // wait that we test already if there is a user
    if (user === null) {
      return
    }
    // set the ref date
    assignData({ referenceDate: moment().subtract(1, 'minutes') })
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
        if (nextUserMediations.length === 0) {
          this.setState({ isLastItem: true })
        }
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
    const { assignData,
      hasFirstItem,
      referenceDate,
      requestData,
      user,
      userMediations
    } = this.props
    const newState = { selectedItem }
    if (user && selectedItem > (hasFirstItem ? 0 : 1) && (selectedItem - 1) === this.state.selectedItem) {
      // update dateRead for previous item
      const previousUserMediationIndex = selectedItem - (hasFirstItem ? 1 : 2)
      console.log('previousUserMediationIndex', previousUserMediationIndex)
      const previousUserMediation = userMediations[previousUserMediationIndex]
      if (previousUserMediation) {
        const { dateRead, id, isFavorite } = previousUserMediation
        // not update if already have one
        if (!dateRead) {
          const nowDate = moment().toISOString()
          const body = [{
            dateRead: nowDate,
            dateUpdated: nowDate,
            id,
            isFavorite
          }]
          // wait a bit to make clear that we load a new set
          setTimeout(() => {
            console.log('previousUserMediation', previousUserMediation)
            requestData('PUT', 'userMediations', { body, sync: true })
          }, 500)
        }
      } else {
        console.warn('previousUserMediation not found')
      }
    } else if (!user &&
      userMediations &&
      selectedItem === userMediations.length &&
      this.state.selectedItem === userMediations.length - 1
    ) {
      const removedIds = userMediations.map(um =>
        um.offer && um.offer.id || um.mediation.offer.id).join('-')
      // wait a bit to make clear that we load a new set
      setTimeout(() => {
        requestData('GET',
          `anonymousOffers?removedIds=${removedIds}`,
          { hook: this.handleOfferToUserMediation }
        )
      }, 500)

    }
    // Ask for older items
    if (!hasFirstItem && selectedItem === 0 && this.state.selectedItem === 1) {
      const unreadOrChangedSince = (userMediations[0].momentDateRead || referenceDate)
                                      .subtract(1, 'm')
                                      .toISOString()
      // wait a bit to make clear that we load a new set
      setTimeout(() => {
        assignData({ referenceDate: unreadOrChangedSince })
        requestData('PUT',
          `userMediations?unreadOrChangedSince=${unreadOrChangedSince}`,
          { sync: true }
        )
      })
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
      this.handleRequestPrevious(nextProps)
      this.setState({ isLastItem: userMediations.slice(-1)[0].isLast })
    }
    if (user !== this.props.user) {
      this.handleRequestData(nextProps)
    }
    // get directly to the not read
    if (user && this.state.selectedItem === 0) {
      // shift
      const selectedItem = Math.max(firstNotReadItem || 0, 0) + (hasFirstItem === false ? 1 : 0)
      this.setState({ selectedItem })
    }
    if (user === false && this.props.user) {
      this.setState({ selectedItem: 0 })
    }
    this.setState({ forcedItem: null })
  }
  render () {
    const { hasFirstItem,
      loadingTag,
      user,
      userMediations
    } = this.props
    const { forcedItem, isLastItem, selectedItem } = this.state
    console.log(selectedItem, 'userMediations', userMediations, 'isLastItem', isLastItem)
    return (
      <div className='explorer mx-auto p2' id='explorer'>
        <div className='explorer__search absolute'>
          <SearchInput collectionName='offers'
            hook={this.handleOfferToUserMediation} />
        </div>
        <Carousel axis='horizontal'
          emulateTouch
          ref={element => this.carouselElement = element}
          selectedItem={forcedItem || selectedItem}
          showArrows={true}
          swipeScrollTolerance={100}
          showStatus={false}
          showIndicators={false}
          showThumbs={false}
          transitionTime={250}
          onChange={this.onChange} >
          {
            loadingTag !== 'search' && userMediations && userMediations.length > 0
              ? (
                  (user && !hasFirstItem &&
                    [<LoadingCard key='first' isForceActive />]) || []
                ).concat(
                  userMediations.map((userMediation, index) =>
                    <Card {...this.state}
                      index={index}
                      itemsCount={userMediations.length}
                      key={index}
                      {...userMediation}
                      {...userMediation.mediation && userMediation.mediation.offer}
                      {...userMediation.offer} />
                  )).concat([
                      isLastItem
                        ? <LastCard key='last' />
                        : <LoadingCard key='next' isForceActive />
                  ])
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
      referenceDate: state.data.referenceDate,
      user: state.user,
      userMediations: state.data.userMediations
    }),
    { assignData, closeLoading, requestData, showLoading }
  ),
  withSelectors({
    userMediations: [
      ownProps => ownProps.referenceDate,
      ownProps => ownProps.user,
      ownProps => ownProps.userMediations,
      (referenceDate, user, userMediations) => {
        // leave if undefined
        if (!userMediations) {
          return userMediations
        }
        // not sort/filter if it is from not connected user
        if (!user) {
          return userMediations
        }
        console.log('AVANT', userMediations)
        // sort given dateRead
        const groupe = groupBy(userMediations,
          um => um.dateRead === null)
        let notReadUms = groupe.get(true)
        // make sure that the isFirst is at the beginning
        notReadUms && notReadUms.sort((um1, um2) => um1.isFirst || um2.isFirst)
        // sort the read ones
        let readUms = groupe.get(false)
        if (!readUms) {
          return notReadUms
        }
        readUms.forEach(readUm => readUm.momentDateRead = moment(readUm.dateRead))
        readUms.sort((um1, um2) => um1.momentDateRead - um2.momentDateRead)
        // filter too old date Read items
        const readUmTuples = readUms && readUms
          .map((readUm, index) => [readUm.momentDateRead, index])
        const firstReadUmTuple = readUmTuples.reverse()
          .find(tuple => tuple[0] < referenceDate)
        if (firstReadUmTuple) {
          console.log('firstReadUmTuple', firstReadUmTuple)
          readUms = readUms.slice(firstReadUmTuple[1])
        }
        // check if there is nothing to read new
        if (!notReadUms) {
          readUms.slice(-1)[0].isLast = true
          return readUms
        }
        // return read - not read items
        return readUms.concat(notReadUms)
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
