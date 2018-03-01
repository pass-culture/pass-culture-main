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
// import { sync } from '../utils/registerDexieServiceWorker'

class UserMediationsExplorer extends Component {
  constructor () {
    super()
    this.state = { carouselElement: null,
      carousselNode: null,
      previousSelectedItem: null,
      selectedCard: null,
      selectedItem: 0
    }
  }
  handleLoading = props => {
    const { cards, closeLoading, showLoading } = props
    if (!cards || cards.length === 0) {
      showLoading()
      return
    }
    closeLoading()
  }
  onChange = selectedItem => {
    const { assignData,
      cards,
      firstCard,
      referenceDate,
      requestData,
      user
    } = this.props
    // init
    const newState = {
      previousSelectedItem: this.state.selectedItem,
      selectedItem
    }
    // NEXT NAVIGATION
    if (selectedItem === this.state.selectedItem + 1) {
      // UPDATE IF THE PREVIOUS UM WAS NOT READ
      if (!this.state.selectedCard.dateRead) {
        const nowDate = moment().toISOString()
        const body = [{
          dateRead: nowDate,
          dateUpdated: nowDate,
          id: this.state.selectedCard.id,
          isFavorite: this.state.selectedCard.isFavorite
        }]
        /*
        // wait a bit to make clear that we load a new set
        requestData('PUT',
          `${collectionName}?around=${}`,
          { body, sync: true }
        )
        */
      }
      // UPDATE SELECTED UM
      const cardIndex = selectedItem - (firstCard ? 0 : 1)
      const selectedCard = cards && cards[cardIndex]
      if (selectedCard) {
        newState.selectedCard = selectedCard
      }
    }
    // LEFT NAVIGATION
    /*
    if (!firstCard && selectedItem === 0 && this.state.selectedItem === 1) {
      const unreadOrChangedSince = (cards[0].momentDateRead || referenceDate)
                                      .subtract(1, 'm')
                                      .toISOString()
      // wait a bit to make clear that we load a new set
      setTimeout(() => {
        assignData({ referenceDate: unreadOrChangedSince })
        requestData('PUT',
          `cards?unreadOrChangedSince=${unreadOrChangedSince}`,
          { sync: true }
        )
      })
    }
    */
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
    this.handleLoading(this.props)
    if (IS_DEV) {
      // this.dexiePullIntervall = setInterval(() => sync('dexie-pull'), 5000)
    }
  }
  componentWillReceiveProps (nextProps) {
    const { cards,
      firstNotReadIndex,
      firstCard,
      user
    } = nextProps
    if (this.carouselElement && cards !== this.props.cards) {
      this.handleLoading(nextProps)
      // be sure to sync the selectedCard with the first not read
      this.setState({
        selectedCard: cards[firstNotReadIndex]
      })
    }
    // init shift
    if (user &&
      cards &&
      !this.state.previousSelectedItem &&
      this.state.selectedItem === 0
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
    if (user === false && this.props.user) {
      this.setState({ previousSelectedItem: null,
        selectedItem: 0,
        selectedCard: null
      })
    }
  }
  componentWillUnmount () {
    if (IS_DEV) {
      //this.dexiePullIntervall && clearInterval(this.dexiePullIntervall)
    }
  }
  render () {
    return <Explorer {...this.props}
      {...this.state}
      searchCollectionName='offers'
      searchHook={this.searchHook} />
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
    cards: [
      ownProps => ownProps.userMediations,
      userMediations => {
        const cards = userMediations && userMediations.map(getCardFromUserMediation)
          .filter(card => card)
        // leave if undefined
        if (!cards) {
          return cards
        }
        // sort given dateRead
        const group = groupBy(cards, card => card.dateRead === null)
        let notReadCards = group[true]
        // sort the read ones
        let readCards = group[false]
        if (!readCards) {
          return notReadCards
        }
        readCards.forEach(readCard => readCard.momentDateRead = moment(readCard.dateRead))
        readCards.sort((card1, card2) => card1.momentDateRead - card2.momentDateRead)
        // check if there is nothing to read new
        if (!notReadCards) {
          readCards.slice(-1)[0].isLast = true
          return readCards
        }
        // return read - not read items
        return readCards.concat(notReadCards)
      }
    ],
    firstCard: [
      (ownProps, nextState) => nextState.cards,
      cards => cards && cards.find(card => card.isFirst)
    ],
    lastCard: [
      (ownProps, nextState) => nextState.cards,
      cards => cards && cards.find(card => card.isLast)
    ],
    firstNotReadIndex: [
      (ownProps, nextState) => nextState.cards,
      cards => cards && cards.map(card => card.dateRead).indexOf(null)
    ]
  })
)(UserMediationsExplorer)
