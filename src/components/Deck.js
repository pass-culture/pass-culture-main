import React, { Component } from 'react'

import Card from './Card'

class Deck extends Component {
  constructor () {
    super()
    this.state = { bufferContents: null,
      cursor: 0,
      deckElement: null,
      isContentChanging: false,
      isTransitioning: false,
      items: null
    }
  }
  handleSetItems = props => {
    // unpack
    const { contents,
      handLength,
      isBlobModel,
    } = props
    const { isContentChanging } = this.state
    // init new state
    // isContentChanging to true helps
    // the card to know that they should not remount with a style transition
    // because they are already at the good place
    const newState = { bufferContents: null,
      isContentChanging: true
    }
    // we need to determine the dynamic mapping
    // of the deck
    if (isBlobModel) {
      // BLOB MODEL
      // the deck has 2 * contents.length
      if (contents) {
        newState.items = [...Array(contents.length).keys()]
          .map(index => -((contents.length - 1)/2) + index)
      }
    } else {
      // SLOT MODEL
      // the deck has 2 * handLength
      // + 2 extra slots helping for buffering on each side
      newState.items = [...Array(2 * handLength + 3).keys()]
          .map(index => - handLength - 1 + index)
    }
    // update
    this.setState(newState)
  }
  onDragCard = (event, data, cursor) => {
    // this.setState({ cursor })
  }
  onNextCard = diffIndex => {
    // unpack
    const { onNextCard,
      onTransition,
      transitionTimeout
    } = this.props
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
  onTransitionEnd = (event, cardProps) => {
    // check and unpack
    const { transitions } = this
    const { contents, onTransitionEnd } = this.props
    const newState = {}
    // update the transitions store
    const newTransitions = [...transitions]
    const transition = newTransitions[cardProps.index]
    // console.log('END', event.propertyName, cardProps.content.id, cardProps.index)
    if (transition && transition[event.propertyName]) {
        delete transition[event.propertyName]
        if (Object.keys(transition).length === 0) {
          newTransitions[cardProps.index] = false
        }
    }
    this.transitions = newTransitions
    // check
    if (newTransitions.every((newTransition, index) => !newTransition)) {
      newState.isTransitioning = false
      this.transitions = null
      // console.log('TRANSITIONS IS OFF')
    }
    // update
    this.setState(newState)
  }
  onTransitionStart = (event, cardProps) => {
    // unpack
    const { transitions } = this
    const { contents } = this.props
    const newState = {}
    // at the first time one of the card is transitioning
    // we init a new array
    let newTransitions
    if (!transitions) {
      newTransitions = [...new Array(contents.length)]
      newState.isTransitioning = true
      // console.log('TRANSITIONS IS ON')
    } else {
      newTransitions = [...transitions]
    }
    // for this particular card, maybe the transition
    // exists alreay or not
    // console.log('START',event.propertyName, cardProps.content.id, cardProps.index)
    const transition = newTransitions[cardProps.index]
    if (!newTransitions[cardProps.index]) {
      newTransitions[cardProps.index] = { [event.propertyName]: true }
    } else {
      newTransitions[cardProps.index][event.propertyName] = true
    }
    this.transitions = newTransitions
    // update
    this.setState(newState)
  }
  componentWillMount () {
    this.handleSetItems(this.props)
  }
  componentWillReceiveProps (nextProps) {
    const { isTransitioning } = this.state
    if (nextProps.contents !== this.props.contents) {
      //console.log(isTransitioning, nextProps.contents.map(content =>
      //  content && `${content.dateRead} ${content.id}` ))
      //console.log(this.props.contents && this.props.contents.map(content =>
      //  content && `${content.dateRead} ${content.id}` ))
      if (isTransitioning) {
        //console.log('WE NOT YET SET ITEMS')
        this.setState({ bufferContents: this.props.contents })
      } else if (!nextProps.isKeepItems) {
        //console.log('WE SET ITEMS')
        this.handleSetItems(nextProps)
      }
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
      onReadCard,
      onTransitionEnd,
      onTransitionStart
    } = this
    const { handLength,
      isBlobModel,
      transitionTimeout,
      readTimeout
    } = this.props
    const { bufferContents,
      cursor,
      deckElement,
      isContentChanging,
      items
    } = this.state
    // console.log('RENDER this.state.bufferContents', this.state.bufferContents)
    // console.log('this.props.contents', this.props.contents)
    const contents = this.state.bufferContents || this.props.contents
    return (
      <div className='deck relative m3'
        ref={_element => this._element = _element }>
        <button className='deck__next deck__next--left button absolute'
          onClick={() => onNextCard(1)}>
          {'<'}
        </button>
        <button className='deck__next deck__next--right button absolute'
          onClick={() => onNextCard(-1)}>
          {'>'}
        </button>
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
              transitionTimeout={transitionTimeout}
              key={index}
              onDrag={onDragCard}
              onNext={onNextCard}
              onRead={onReadCard}
              onTransitionEnd={onTransitionEnd}
              onTransitionStart={onTransitionStart}
              readTimeout={readTimeout} />
          )
        }
      </div>
    )
  }
}

Deck.defaultProps = { deckKey: 0,
  handLength: 2,
  isBlobModel: false,
  readTimeout: 3000,
  transitionTimeout: 500
}

export default Deck
