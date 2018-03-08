import React, { Component } from 'react'

import Card from './Card'

class Deck extends Component {
  constructor () {
    super()
    this.state = { cursor: 0,
      deckElement: null,
      isContentChanging: false,
      items: null
    }
  }
  handleSetItems = props => {
    // unpack
    const { contents,
      handLength,
      isBlobModel
    } = props
    // we need to determine the dynamic mapping
    // of the deck
    if (isBlobModel && contents) {
      // BLOB MODEL
      // the deck has 2 * contents.length
      this.setState({
        items: [...Array(contents.length).keys()]
          .map(index => -((contents.length - 1)/2) + index),
      })
    } else {
      // SLOT MODEL
      // the deck has 2 * handLength
      // + 2 extra slots helping for buffering on each side
      this.setState({
        items: [...Array(2 * handLength + 3).keys()]
          .map(index => - handLength - 1 + index),
        isContentChanging: true
      })
    }
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
      this.handleSetItems(this.props)
    }
  }
  componentDidMount () {
    this.setState({ deckElement: this._element })
    if (this.state.isContentChanging) {
      setTimeout(() => this.setState({ isContentChanging: false }), 10)
    }
  }
  componentDidUpdate (prevProps, prevState) {
    // unpack
    const { isContentChanging } = this.state
    // the deck updated because we changed the contents
    // so we need to wait just the refresh of the children
    // card to reset to false the isContentChanging
    if (isContentChanging && !prevState.isContentChanging) {
      setTimeout(() => this.setState({ isContentChanging: false }), 10)
    }
  }
  render () {
    const { onDragCard,
      onNextCard,
      onReadCard
    } = this
    const { contents,
      handLength,
      isBlobModel,
      nextTimeout
    } = this.props
    const { cursor,
      deckElement,
      isContentChanging,
      items
    } = this.state
    console.log('BEN', isContentChanging)
    return (
      <div className='deck relative m3'
        ref={_element => this._element = _element }>
        {
          items && items.map((item, index) =>
            contents && contents[index] && <Card content={contents && contents[index]}
              contentLength={contents && contents.length}
              cursor={cursor}
              deckElement={deckElement}
              handLength={handLength}
              isBlobModel={isBlobModel}
              isContentChanging={isContentChanging}
              isFirst={contents && !contents[index - 1]}
              isLast={contents && !contents[index + 1]}
              index={index}
              item={item}
              nextTimeout={nextTimeout}
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

Deck.defaultProps = { deckKey: 0,
  handLength: 2,
  isBlobModel: false,
  nextTimeout: 500
}

export default Deck
