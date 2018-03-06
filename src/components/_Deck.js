import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Card from './Card'

class Deck extends Component {
  handle
  render () {
    const { size } = this.props
    const lastKey = 2 * size + 1
    const indexes = [...Array(size).keys()]
    console.log('indexes', indexes)
    return (
      <div>
        {
          [
            <Card index={0} key={0} />,
            ...indexes.map(index => {
              const key = index + 1
              return <Card index={key} key={key} />
            }),
            <Card key={size + 1} />,
            ...indexes.map(index => {
              const key = size + 2 + index
              return <Card index={key} key={key} />
            }),
            <Card index={lastKey} key={lastKey} />
          ]
        }
      </div>
    )
  }
}

Deck.defaultProps = {
  size: 2
}

export default Deck
/*
export default compose(
  connect(
    state => ({
      cards: state.data.userMediations
    })
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
    ]
  })
)(Deck)
*/
