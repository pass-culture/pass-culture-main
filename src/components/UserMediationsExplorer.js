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
  onChange = nextSelectedItem => {
    const { assignData,
      cards,
      firstCard,
      loadingTimeout,
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
      console.log('selectedCard', selectedCard)
      if (selectedCard && !selectedCard.dateRead) {
        const nowDate = moment().toISOString()
        const body = [{
          dateRead: nowDate,
          dateUpdated: nowDate,
          id: selectedCard.id,
          isFavorite: selectedCard.isFavorite
        }]
        // wait a bit to make clear that we load a new set
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
    this.handleLoading(this.props)
    if (IS_DEV) {
      // this.dexiePullIntervall = setInterval(() => sync('dexie-pull'), 5000)
    }
  }
  componentWillReceiveProps (nextProps) {
    const { cards,
      firstNotReadIndex,
      firstCard,
      loadingTimeout,
      user
    } = nextProps
    const { hasPushPullRequested, selectedItem } = this.state
    if (cards !== this.props.cards) {
      this.handleLoading(nextProps)
      // be sure to sync the selectedCard with the first not read
      this.setState({ selectedCard: cards[firstNotReadIndex] })
      // ALMOST END NAVIGATION
      if (!hasPushPullRequested && selectedItem > cards.length - 1) {
        // wait a bit to make clear that we load a new set
        setTimeout(() => sync('dexie-push-pull'), loadingTimeout)
        this.setState({ hasPushPullRequested: true })
      } else {
        this.setState({ hasPushPullRequested: false })
      }
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
    console.log('ON SE CASSE')
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
  loadingTimeout: 500
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
    ]
  })
)(UserMediationsExplorer)
