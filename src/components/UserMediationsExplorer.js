import groupBy from 'lodash.groupby'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Explorer from './Explorer'
import withSelectors from '../hocs/withSelectors'
import { assignData, requestData } from '../reducers/data'
import { closeLoading, showLoading } from '../reducers/loading'
import { getCardFromUserMediation } from '../utils/cards'
import { IS_DEV } from '../utils/config'
import { sync } from '../utils/registerDexieServiceWorker'

class UserMediationsExplorer extends Component {
  constructor () {
    super()
    this.state = { hasPushPullRequested: false,
      isFading: false,
      isLast: false,
      isNewReading: false,
      isReordering: false,
      previousSelectedItem: null,
      selectedCard: null,
      selectedItem: 0
    }
  }
  handleAskMoreCards = props => {
    // unpack
    const { cards,
      loadingTimeout,
      pushPullIndex
    } = props
    const { isLast,
      hasPushPullRequested,
      selectedItem
    } = this.state
    const newState = {}
    // ALMOST END NAVIGATION
    // when we have few still cards in the end
    // meaning we should force a dexie push pull
    // in order to ask for more cards
    if (selectedItem > cards.length - pushPullIndex) {
      // be sure that we have not yet asked for that
      if (!isLast && !hasPushPullRequested) {
        // wait a bit to make clear that we load a new set
        setTimeout(() => sync('dexie-push-pull'), loadingTimeout)
        // be sure to not request one more time
        // when one push pull is already triggered
        newState.hasPushPullRequested = true
      } else {
        newState.hasPushPullRequested = false
        newState.isLast = true
      }
    } else {
      newState.hasPushPullRequested = false
    }
    // update
    this.setState(newState)
  }
  handleInitLoading = props => {
    const { cards, closeLoading, showLoading } = props
    if (!cards || cards.length === 0) {
      showLoading()
      return
    }
    closeLoading()
  }
  handleInitFirstItem = props => {
    // unpack
    const { cards,
      firstCard,
      firstNotReadIndex,
      user
    } = props
    const { previousSelectedItem,
      selectedItem
    } = this.state
    // VERY FIRST SITUATION
    // when cards are just first loaded
    // we trigger the fact to go
    if (user && cards &&
      !previousSelectedItem &&
      selectedItem === 0 &&
      firstNotReadIndex > -1
    ) {
      // get directly to the not read
      let selectedItem = firstNotReadIndex + (firstCard ? 0 : 1)
      let selectedCard = cards[firstNotReadIndex]
      // but if there is no more card to be read... go to the last one
      if (firstNotReadIndex === -1) {
        selectedItem = cards.length - 1 + (firstCard ? 0 : 1)
        selectedCard = cards[cards.length - 1]
      }
      // update
      this.setState({ selectedItem, selectedCard })
    }
  }
  handleReorderLoading = nextProps => {
    // unpack
    const { cards,
      closeLoading,
      firstNotReadItem,
      showLoading
    } = nextProps
    const { selectedItem } = this.state
    // TRANSITION OF BLOBS
    // when the actual item is actually after the firstNotReadItem
    // it is actually a transition situation
    // we should not be there
    if (firstNotReadItem > -1 && selectedItem > firstNotReadItem) {
      // put in buffer the previous cards
      // there will be overriden the props.cards one
      // during a certain moment
      // preventing the Carousel to update the view
      this.setState({ cards: this.props.cards,
        isFading: true
      })
      showLoading()
      // first timeout to trigger the fade out
      // of the current carousel
      setTimeout(() => {
        this.setState({ isReordering: true })
        // second timeout to trigger the next new fresh
        // carousel with the new cards at the good cursor
        setTimeout(() => {
          closeLoading()
          this.setState({
            cards,
            isFading: false,
            isReordering: false,
            selectedItem: firstNotReadItem
          })
        }, 500)
      }, 500)
    }
  }
  handleLogoutUser = props => {
    const { user } = props
    // reset when reset user
    if (user === false && this.props.user) {
      this.setState({ previousSelectedItem: null,
        selectedItem: 0,
        selectedCard: null
      })
    }
  }
  onChange = nextSelectedItem => {
    // unpack
    const { assignData,
      cards,
      firstCard,
      loadingTimeout,
      newReadingTimeout,
      referenceDate,
      requestData,
      user
    } = this.props
    const { selectedCard, selectedItem } = this.state
    // init
    const newState = { previousSelectedItem: selectedItem,
      selectedItem: nextSelectedItem
    }
    // NEXT NAVIGATION
    if (nextSelectedItem === selectedItem + 1) {
      // UPDATE IF THE PREVIOUS UM WAS NOT READ
      if (selectedCard && !selectedCard.dateRead) {
        // FORCE TO STAY A BIT HERE BY SETTING a state variable
        newState.isNewReading = true
        setTimeout(() =>
          this.setState({ isNewReading: false }), newReadingTimeout)
        // UPDATE DEXIE
        const nowDate = moment().toISOString()
        const body = [{
          dateRead: nowDate,
          dateUpdated: nowDate,
          id: selectedCard.id,
          isFavorite: selectedCard.isFavorite
        }]
        requestData('PUT', 'userMediations', { body, sync: true })
      }
    }
    // LEFT NAVIGATION
    if (nextSelectedItem === selectedItem - 1) {
      if (!firstCard && nextSelectedItem === 0 && selectedItem === 1) {
        // wait a bit to make clear that we load a new set
        setTimeout(() =>
          sync('dexie-push-pull', { around: cards[0].id }), loadingTimeout)
      }
    }
    // UPDATE THE SELECTED CARD
    const nextCardIndex = nextSelectedItem - (firstCard ? 0 : 1)
    const nextSelectedCard = cards && cards[nextCardIndex]
    if (nextSelectedCard) {
      newState.selectedCard = nextSelectedCard
    }
    // UPDATE
    this.setState(newState)
  }
  // from a search this function helps to wrap
  // the data into convenient user mediations
  searchHook = (method, path, result, config) => {
    const { assignData,
      cards,
      getEntityFromCard,
      user,
      requestData
    } = this.props
    if (!result.data) {
      return
    }
    if (config.value && config.value.length > 0) {
      const nextData = result.data.map(offer => ({
        isClicked: false,
        isFavorite: false,
        offer
      }))
      assignData({ userMediations: nextData })
    } else if (user) {
      requestData('PUT', 'userMediations', { sync: true })
    }
  }
  componentWillMount () {
    this.handleInitLoading(this.props)
  }
  componentWillReceiveProps (nextProps) {
    // unpack
    const { cards } = nextProps
    // when the cards have changed
    if (cards !== this.props.cards) {
      this.handleInitLoading(nextProps)
      this.handleReorderLoading(nextProps)
      this.handleAskMoreCards(nextProps)
    }
    this.handleInitFirstItem(nextProps)
    this.handleLogoutUser(nextProps)
  }
  render () {
    return <Explorer {...this.props}
      {...this.state}
      onChange={this.onChange}
      searchCollectionName='offers'
      searchHook={this.searchHook} />
  }
}

UserMediationsExplorer.defaultProps = {
  loadingTimeout: 500,
  newReadingTimeout: 10,
  //newReadingTimeout: 500,
  pushPullIndex: 10,
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
    cards: [
      ownProps => ownProps.userMediations,
      userMediations => {
        // init
        if (!userMediations) {
          return
        }
        let cards
        // convert and group
        const group = groupBy(userMediations.map(getCardFromUserMediation),
          card => card.dateRead === null)
        // sort the read ones
        const readCards = group[false]
        if (readCards) {
          readCards.forEach(readCard =>
            readCard.momentDateRead = moment(readCard.dateRead))
          readCards.sort((card1, card2) =>
            card1.momentDateRead - card2.momentDateRead)
          cards = readCards
        } else {
          cards = []
        }
        const notReadCards = group[true]
        if (notReadCards) {
          notReadCards.forEach(notReadCard =>
            notReadCard.momentDateUpdated = moment(notReadCard.dateUpdated))
          notReadCards.sort((card1, card2) =>
            card1.momentDateUpdated - card2.momentDateUpdated)
          cards = cards.concat(notReadCards)
        }
        // return
        return cards
      }
    ],
    firstCard: [
      (ownProps, nextState) => nextState.cards,
      cards => cards && cards.find(card => card.isFirst)
    ],
    firstNotReadIndex: [
      (ownProps, nextState) => nextState.cards,
      cards => cards && cards.map(card => card.dateRead).indexOf(null)
    ],
    firstNotReadItem: [
      (ownProps, nextState) => nextState.firstCard,
      (ownProps, nextState) => nextState.firstNotReadIndex,
      (firstCard, firstNotReadIndex) => firstNotReadIndex + (firstCard ? 0 : 1)
    ]
  })
)(UserMediationsExplorer)
