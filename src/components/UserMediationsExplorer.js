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
  handleInitLoading = props => {
    const { cards, closeLoading, showLoading } = props
    if (!cards || cards.length === 0) {
      showLoading()
      return
    }
    closeLoading()
  }
  handleReorderLoading = nextProps => {
    const { cards,
      closeLoading,
      firstNotReadItem,
      showLoading
    } = nextProps
    this.setState({ cards: this.props.cards,
      isFading: true
    })
    showLoading()
    setTimeout(() => {
      this.setState({ isReordering: true })
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
  onChange = nextSelectedItem => {
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
        // FORCE TO STAY A BIT
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
    // UPDATE SELECTED UM
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
    const { cards,
      closeLoading,
      firstNotReadIndex,
      firstNotReadItem,
      firstCard,
      loadingTimeout,
      pushPullIndex,
      showLoading,
      user
    } = nextProps
    const { hasPushPullRequested,
      isLast,
      previousSelectedItem,
      selectedCard,
      selectedItem
    } = this.state
    if (cards !== this.props.cards) {
      this.handleInitLoading(nextProps)
      // init new state and be sure to sync the selectedCard with the first not read
      const selectedCard = cards[firstNotReadIndex]
      const newState = {
        selectedCard
      }
      // we need to reorder and that transition is ont smooth
      // so let's assume it
      if (firstNotReadItem > -1 && selectedItem > firstNotReadItem) {
        this.handleReorderLoading(nextProps)
      }
      // ALMOST END NAVIGATION
      if (selectedItem > cards.length - pushPullIndex) {
        if (!isLast && !hasPushPullRequested) {
          // wait a bit to make clear that we load a new set
          setTimeout(() => sync('dexie-push-pull'), loadingTimeout)
          // be sure to not request one more time when one push pull is already triggered
          newState.hasPushPullRequested = true
        } else {
          newState.hasPushPullRequested = false
          newState.isLast = true
        }
        // the blobs is going to have more un read elements
        // so we need to sync again the selected item by going back
        if (selectedItem > firstNotReadItem) {
          if (firstNotReadIndex > -1) {
            // newState.selectedItem = firstNotReadItem
            this.handleReorderLoading(nextProps)
          }
        }
      } else {
        newState.hasPushPullRequested = false
      }
      // update
      this.setState(newState)
    }
    // init shift
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
    // reset when reset user
    if (user === false && this.props.user) {
      this.setState({ previousSelectedItem: null,
        selectedItem: 0,
        selectedCard: null
      })
    }
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
  newReadingTimeout: 500,
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
