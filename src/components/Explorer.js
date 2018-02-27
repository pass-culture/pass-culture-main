import groupBy from 'lodash.groupby'
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
      previousSelectedItem: null,
      selectedUserMediation: null,
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
    const { hasFirst, userMediations } = props
    if (userMediations &&
      this.props.userMediations &&
      this.props.userMediations.length < userMediations.length &&
      this.props.userMediations[0]
    ) {
      let forcedItem = userMediations &&
        userMediations.indexOf(this.props.userMediations[0])
      if (forcedItem > 0) {
        if (!hasFirst) {
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
    requestData('GET', 'userMediations', { sync: true })
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
    if (config.value && config.value.length > 0) {
      let nextUserMediations = result.data.map(offer => ({
        isClicked: false,
        isFavorite: false,
        offer
      }))
      assignData({ userMediations: nextUserMediations })
    } else if (user) {
      requestData('PUT', 'userMediations', { sync: true })
    }
  }
  onChange = selectedItem => {
    const { assignData,
      hasFirst,
      referenceDate,
      requestData,
      user,
      userMediations
    } = this.props
    // init
    const newState = {
      previousSelectedItem: this.state.selectedItem,
      selectedItem
    }
    // NEXT NAVIGATION
    if (selectedItem === this.state.selectedItem + 1) {
      // UPDATE IF THE PREVIOUS UM WAS NOT READ
      if (!this.state.selectedUserMediation.dateRead) {
        const nowDate = moment().toISOString()
        const body = [{
          dateRead: nowDate,
          dateUpdated: nowDate,
          id: this.state.selectedUserMediation.id,
          isFavorite: this.state.selectedUserMediation.isFavorite
        }]
        // wait a bit to make clear that we load a new set
        requestData('PUT',
          `userMediations?unreadOrChangedSince=${referenceDate.toISOString()}`,
          { body, sync: true }
        )
      }
      // UPDATE SELECTED UM
      const userMediationIndex = selectedItem - (hasFirst ? 0 : 1)
      const selectedUserMediation = userMediations &&
        userMediations[userMediationIndex]
      if (selectedUserMediation) {
        newState.selectedUserMediation = selectedUserMediation
      }
    }
    // LEFT NAVIGATION
    /*
    if (!hasFirst && selectedItem === 0 && this.state.selectedItem === 1) {
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
    */
    // UPDATE
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
      firstNotReadUserMediationIndex,
      hasFirst,
      hasLast,
      user,
      userMediations
    } = nextProps
    if (this.carouselElement && userMediations !== this.props.userMediations) {
      this.handleLoading(nextProps)
      this.handleRequestPrevious(nextProps)
      // be sure to sync the selectedUserMediation with the first not read
      // console.log('firstNotReadUserMediationIndex', firstNotReadUserMediationIndex, this.state.selectedItem)
      this.setState({
        // selectedItem: firstNotReadItem,
        selectedUserMediation: userMediations[firstNotReadUserMediationIndex]
      })
    }
    if (user !== this.props.user) {
      this.handleRequestData(nextProps)
    }
    // init shift
    if (user &&
      userMediations &&
      !this.state.previousSelectedItem &&
      this.state.selectedItem === 0
    ) {
      // get directly to the not read
      let selectedItem = firstNotReadUserMediationIndex
      let selectedUserMediation = userMediations[firstNotReadUserMediationIndex]
      // but if there is no more card to be read... go to the last one
      if (firstNotReadUserMediationIndex === -1) {
        selectedItem = userMediations.length - 1 + (hasFirst ? 0 : 1)
        selectedUserMediation = userMediations[userMediations.length - 1]
      }
      // update
      this.setState({ selectedItem, selectedUserMediation })
    }
    if (user === false && this.props.user) {
      this.setState({
        previousSelectedItem: null,
        selectedItem: 0,
        selectedUserMediation: null
      })
    }
  }
  render () {
    const { hasFirst,
      hasLast,
      loadingTag,
      userMediations
    } = this.props
    const { selectedItem } = this.state
    console.log('render', selectedItem, userMediations)
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
              ? ((!hasFirst && [<LoadingCard key='first' isForceActive />]) || [])
                .concat(
                  userMediations.map((userMediation, index) =>
                    <Card {...this.state}
                      index={index}
                      itemsCount={userMediations.length}
                      key={index}
                      {...userMediation}
                      {...userMediation.mediation && userMediation.mediation.offer}
                      {...userMediation.offer} />
                  )).concat([
                      hasLast
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
      ownProps => ownProps.userMediations,
      (referenceDate, userMediations) => {
        // leave if undefined
        if (!userMediations) {
          return userMediations
        }
        // sort given dateRead
        const group = groupBy(userMediations,
          um => um.dateRead === null)
        let notReadUms = group[true]
        // make sure that the isFirst is at the beginning
        notReadUms && notReadUms.sort((um1, um2) => um1.isFirst || um2.isFirst)
        // sort the read ones
        let readUms = group[false]
        if (!readUms) {
          return notReadUms
        }
        readUms.forEach(readUm => readUm.momentDateRead = moment(readUm.dateRead))
        readUms.sort((um1, um2) => um1.momentDateRead - um2.momentDateRead)
        // check if there is nothing to read new
        if (!notReadUms) {
          readUms.slice(-1)[0].isLast = true
          return readUms
        }
        // return read - not read items
        return readUms.concat(notReadUms)
      }
    ],
    hasFirst: [
      (ownProps, nextState) => nextState.userMediations,
      userMediations => userMediations &&
        userMediations[0] &&
        userMediations[0].isFirst
    ],
    hasLast: [
      (ownProps, nextState) => nextState.userMediations,
      userMediations => userMediations &&
        userMediations.slice(-1)[0] &&
        userMediations.slice(-1)[0].isLast
    ],
    firstNotReadUserMediationIndex: [
      (ownProps, nextState) => nextState.userMediations,
      userMediations => userMediations &&
          userMediations.map(um => um.dateRead)
                        .indexOf(null)
    ],
    firstNotReadItem: [
      (ownProps, nextState) => nextState.hasFirst,
      (ownProps, nextState) => nextState.firstNotReadUserMediationIndex,
      (hasFirst, firstNotReadUserMediationIndex) =>
        firstNotReadUserMediationIndex + (hasFirst === false ? 1 : 0)
    ]
  }),
)(Explorer)
