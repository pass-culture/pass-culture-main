import React, { Component } from 'react'

import Card from './Card'

class Deck extends Component {
  constructor () {
    super()
    this.state = { cursor: 0,
      deckElement: null,
      items: null
    }
  }
  handleSetItems = props => {
    const { items, size } = props
    this.setState({ items: items || [...Array(2* size + 3).keys()] })
  }
  onDragCard = (event, data) => {
    this.setState({ cursor: data.x / (this._element.offsetWidth / 2) })
  }
  onNextCard = diffIndex => {
    // unpack
    const { onNextCard } = this.props
    const { items } = this.state
    // update by shifting the items
    this.setState({ cursor: 0,
      items: items.map(index => index + diffIndex)
    })
    // hook if Deck has parent manager component
    onNextCard && onNextCard(diffIndex, this.props, this.state)
  }
  onReadCard = card => {
    // unpack
    const { onReadCard } = this.props
    // hook if Deck has parent manager component
    onReadCard && onReadCard(card)
  }
  componentWillMount () {
    this.handleSetItems(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.size !== this.props.size) {
      this.handleSetItems(nextProps)
    }
  }
  componentDidMount () {
    this.setState({ deckElement: this._element })
  }
  render () {
    const { onDragCard,
      onNextCard,
      onReadCard
    } = this
    const { contents, size } = this.props
    const { cursor,
      deckElement,
      items
    } = this.state
    return (
      <div className='deck relative m3'
        ref={_element => this._element = _element }>
        {
          items.map((item, index) =>
            <Card content={contents && contents[index]}
              cursor={cursor}
              deckElement={deckElement}
              isAround={item === size + 1}
              isFirst={contents && contents[index] && !contents[index - 1]}
              isLast={contents && contents[index] && !contents[index + 1]}
              index={index}
              item={item}
              key={index}
              onDrag={onDragCard}
              onNext={onNextCard}
              onRead={onReadCard}
              size={size} />
          )
        }
      </div>
    )
  }
}

Deck.defaultProps = {
  size: 2
}

export default Deck
