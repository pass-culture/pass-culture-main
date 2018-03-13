import classnames from 'classnames'
import debounce from 'lodash.debounce'
import React, { Component } from 'react'

import Card, { CURRENT } from './Card'

class Deck extends Component {
  constructor (props) {
    super(props)
    this.state = { bufferContents: null,
      cursor: 0,
      deckElement: null,
      isContentChanging: false,
      isFirstCard: false,
      isLastCard: false,
      isResizing: false,
      isTransitioning: false,
      items: null
    }
    this.onDebouncedResize = debounce(this.onResize, props.resizeTimeout)
  }
  handleSetTypeCard = (type, cardProps) => {
    if (type !== CURRENT) {
      return
    }
    const newState = {
      isFirstCard: false,
      isLastCard: false
    }
    if (cardProps.isFirst) {
      newState.isFirstCard = true
    } else if (cardProps.isLast) {
      newState.isLastCard = true
    }
    this.setState(newState)
  }
  handleNextItemCard = diffIndex => {
    // unpack
    const { contents, handLength, handleNextItemCard } = this.props
    const { items } = this.state
    // check
    console.log('items[0]', items[0], contents.length)
    console.log('items.slice(-1)[0]', items.slice(-1)[0], contents.length)
    if (diffIndex > 0 && items[0] < -contents.length - handLength) {
      console.log('STOP 1')
    } else if (diffIndex < 0 && items.slice(-1)[0] > contents.length + handLength) {
      console.log('STOP 2')
    }
    // update by shifting the items
    this.setState({ cursor: 0,
      items: items.map(index => index + diffIndex)
    })
    // hook if Deck has parent manager component
    handleNextItemCard && handleNextItemCard(diffIndex, this.props, this.state)
  }
  handleSetItems = props => {
    // unpack
    const { aroundIndex,
      contents,
      handLength,
      isBlobModel,
    } = props
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
        // const halfLength = Math.floor((contents.length + 1)/2)
        // newState.items = [...Array(contents.length).keys()]
        //  .map(index => - halfLength - 1 + index)
        newState.items = [...Array(contents.length).keys()]
          .map(index => - handLength - 1 - (aroundIndex > 0 ? aroundIndex : 0) + index)
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
  handleSetReadCard = card => {
    // unpack
    const { handleSetReadCard } = this.props
    // hook if Deck has parent manager component
    handleSetReadCard && handleSetReadCard(card)
  }
  onDragCard = (event, data, cursor) => {
    // this.setState({ cursor })
  }
  onResize = event => {
    this.setState({ isResizing: true })
  }
  onTransitionEnd = (event, cardProps) => {
    // check and unpack
    const { transitions } = this
    // update the transitions store
    if (!transitions) {
      console.warn('transitions is null while we try to update transition end...? weird')
      return
    }
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
      this.setState({ isTransitioning: false })
      this.transitions = null
      // console.log('TRANSITIONS IS OFF')
    }
  }
  onTransitionStart = (event, cardProps) => {
    // unpack
    const { transitions } = this
    const { contents } = this.props
    // at the first time one of the card is transitioning
    // we init a new array
    let newTransitions
    if (!transitions) {
      newTransitions = [...new Array(contents.length)]
      this.setState({ isTransitioning: true })
      // console.log('TRANSITIONS IS ON')
    } else {
      newTransitions = [...transitions]
    }
    // for this particular card, maybe the transition
    // exists alreay or not
    // console.log('START',event.propertyName, cardProps.content.id, cardProps.index)
    if (!newTransitions[cardProps.index]) {
      newTransitions[cardProps.index] = { [event.propertyName]: true }
    } else {
      newTransitions[cardProps.index][event.propertyName] = true
    }
    this.transitions = newTransitions
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
    window.addEventListener('resize', this.onDebouncedResize)
  }
  componentDidUpdate (prevProps, prevState) {
    // unpack
    const { isContentChanging, isResizing, isTransitioning } = this.state
    // the deck updated because we changed the contents
    // so we need to wait just the refresh of the children
    // card to reset to false the isContentChanging
    if (isContentChanging && !prevState.isContentChanging) {
      setTimeout(() => this.setState({ isContentChanging: false }), 10)
    }
    // as the deck element has a dynamical width
    // we need to trigger again the set of the style
    //o the children when we resize the window
    if (isResizing && !prevState.isResizing) {
      this.setState({ isResizing: false })
    }
    // during the transition maybe we kept some buffer contents
    // and now we can peacefully release the next one
    // by also sync the items again
    if (!isTransitioning && prevState.isTransitioning) {
      this.handleSetItems(this.props)
      this.setState({ bufferContents: null })
    }
  }
  componentWillUnmount () {
    window.removeEventListener('resize', this.onDebouncedResize)
  }
  render () {
    const { handleSetTypeCard,
      handleSetReadCard,
      handleNextItemCard,
      onDragCard,
      onTransitionEnd,
      onTransitionStart
    } = this
    const { handLength,
      isBlobModel,
      transitionTimeout,
      readTimeout
    } = this.props
    const { cursor,
      deckElement,
      isContentChanging,
      isFirstCard,
      isLastCard,
      isResizing,
      items
    } = this.state
    const contents = this.state.bufferContents || this.props.contents
    // console.log('')
    // console.log('RENDER DECK this.state.bufferContents', this.state.bufferContents && this.state.bufferContents.length,
    // this.state.bufferContents && this.state.bufferContents.map(content => content && `${content.id} ${content.dateRead}`))
    // console.log('RENDER DECK this.props.contents', this.props.contents && this.props.contents.length,
    // this.props.contents && this.props.contents.map(content => content && `${content.id} ${content.dateRead}`))
    // console.log('RENDER DECK contents', contents && contents.length,
    // contents && contents.map(content => content && `${content.id} ${content.dateRead}`))
    // console.log('RENDER DECK', 'this.state.items', this.state.items)
    return (
      <div className='deck relative m3'
        ref={_element => this._element = _element }>
        <button className={classnames('deck__next deck__next--left button absolute', {
          'button--disabled': isFirstCard })}
          onClick={() => handleNextItemCard(1)}
          disabled={isFirstCard} >
          {'<'}
        </button>
        <button className={classnames('deck__next deck__next--right button absolute', {
          'button--disabled': isLastCard })}
          onClick={() => handleNextItemCard(-1)}
          disabled={isLastCard} >
          {'>'}
        </button>
        {
          items && items.map((item, index) =>
            contents && contents[index] && <Card content={contents && contents[index]}
              contentLength={contents && contents.length}
              cursor={cursor}
              deckElement={deckElement}
              handLength={handLength}
              handleNextItem={handleNextItemCard}
              handleSetRead={handleSetReadCard}
              handleSetType={handleSetTypeCard}
              isBlobModel={isBlobModel}
              isContentChanging={isContentChanging}
              isFirst={contents && !contents[index - 1]}
              isLast={contents && !contents[index + 1]}
              index={index}
              isResizing={isResizing}
              item={item}
              transitionTimeout={transitionTimeout}
              key={index}
              onDrag={onDragCard}
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
  resizeTimeout: 500,
  transitionTimeout: 500
}

export default Deck
