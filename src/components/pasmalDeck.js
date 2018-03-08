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
    const { contents } = props
    if (!contents) {
      return
    }
    this.setState({
      items: [...Array(contents.length).keys()]
                .map(index => -((contents.length - 1)/2) + index)
    })
  }
  onDragCard = (event, data, cursor) => {
    // this.setState({ cursor })
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
    if (nextProps.contents !== this.props.contents) {
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
    const { contents, handLength } = this.props
    const { cursor,
      deckElement,
      items
    } = this.state
    console.log('contents', contents)
    return (
      <div className='deck relative m3'
        ref={_element => this._element = _element }>
        {
          contents && contents.map((content, index) =>
            content && <Card content={content}
              contentLength={contents.length}
              cursor={cursor}
              deckElement={deckElement}
              handLength={handLength}
              isFirst={content && !contents[index - 1]}
              isLast={content && !contents[index + 1]}
              index={index}
              item={items[index]}
              key={index}
              onDrag={onDragCard}
              onNext={onNextCard}
              onRead={onReadCard} />
          )
        }
      </div>
    )
  }
}

Deck.defaultProps = {
  handLength: 2
}

export default Deck
