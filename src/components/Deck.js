import classnames from 'classnames'
import Draggable from 'react-draggable'
import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { rgb_to_hsv } from 'colorsys'

import Card, { AROUND } from './Card'
import Icon from './Icon'

class Deck extends Component {
  constructor (props) {
    super(props)
    this.state = { bufferContents: null,
      currentContent: null,
      cursor: 0,
      deckElement: null,
      transition: null,
      isFirstCard: false,
      isFlipping: false,
      isLastCard: false,
      isResizing: false,
      isTransitioning: false,
      isVerso: false,
      items: null
    }
    this.onDebouncedResize = debounce(this.onResize, props.resizeTimeout)
  }
  handleSetTypeCard = (cardProps, cardState) => {
    // only set things for the current Card
    if (cardState.type !== AROUND) {
      return
    }
    this.props.isDebug && console.log('DEBUG: Deck - handleSetTypeCard')
    // no need to set in state the current cardProps
    this.currentCardProps = cardProps
    this.currentCardState = cardState
    const newState = { isFirstCard: false,
      isLastCard: false
    }
    if (cardProps.isFirst) {
      newState.isFirstCard = true
    } else if (cardProps.isLast) {
      newState.isLastCard = true
    }
    // update
    this.setState(newState)
  }
  handleNextItemCard = diffIndex => {
    // unpack
    const { handleNextItemCard, isDebug } = this.props
    const { items } = this.state
    if (!items) {
      console.warn('items is not defined')
      return
    }
    isDebug && console.log('DEBUG: Deck - handleNextItemCard')
    // new state
    this.items = items.map(index => index + diffIndex)
    const newState = { cursor: 0,
      items: this.items
    }
    // update by shifting the items
    this.setState(newState)
    // hook if Deck has parent manager component
    handleNextItemCard && handleNextItemCard(diffIndex, this)
  }
  handleRelaxItemCard = data => {
    this.props.isDebug && console.log('DEBUG: Deck - handleResetItemCard')
    this.setState({ cursor: 0 })
  }
  handleResetItems = (config = {}) => {
    // unpack
    const { isDebug } = this.props
    const contents = config.contents || this.props.contents
    const aroundIndex = config.aroundIndex || this.props.aroundIndex
    if (!contents) {
      return
    }
    isDebug && console.log(`DEBUG: Deck - handleResetItems aroundIndex=${aroundIndex}`)
    // we need to determine the dynamic mapping of the deck
    const items = [...Array(contents.length).keys()]
      .map(index => index - (aroundIndex > 0 ? aroundIndex : 0))
    this.items = items
    // update
    this.setState({ items })
  }
  handleSetCurrentContent = () => {
    // unpack
    const { items } = this
    const { contents, isDebug } = this.props
    isDebug && console.log('DEBUG: Deck - handleSetCurrentContent')
    // find
    const aroundIndex = items && items.indexOf(0)
    const currentContent = contents && contents[aroundIndex]
    this.currentContent = currentContent
    // update
    this.setState({ currentContent })
  }
  handleSetStyle = () => {
    // unpack
    const { currentContent } = this
    const { transitionTimeout } = this.props
    // style
    const buttonStyle = { transition: `opacity ${transitionTimeout}ms` }
    const style = {
      backgroundColor: 'black',
      transition: `background-color ${transitionTimeout}ms`
    }
    const gradientStyle = {
      background: 'linear-gradient(transparent, black)',
      transition: `background ${transitionTimeout}ms`
    }
    if (currentContent && currentContent.backgroundColor) {
      const [red, green, blue] = currentContent.backgroundColor
      const hue = rgb_to_hsv({r: red, g: green, b: blue}).h
      style.backgroundColor = `hsl(${hue}, 100%, 15%)`
      gradientStyle.background = `linear-gradient(transparent, hsl(${hue}, 100%, 15%))`
    }
    // update
    this.setState({ buttonStyle, gradientStyle, style })
  }
  handleSetReadCard = card => {
    // unpack
    const { handleSetReadCard, isDebug } = this.props
    isDebug && console.log('DEBUG: Deck - handleSetReadCard')
    // hook if Deck has parent manager component
    handleSetReadCard && handleSetReadCard(card)
  }
  handleSetCursorCard = cursor => {
    this.props.isDebug && console.log('DEBUG: Deck - handleSetCursorCard')
    this.setState({ cursor, transition: 'none' })
  }
  handleFlipCard = () => {
    this.setState({ isVerso: !this.state.isVerso })
  }
  onStart = (event, data) => {
    this.props.isDebug && console.log('DEBUG: Deck - onStart')
    this.setState({ isFlipping: true, clientY: event.clientY })
  }
  onDrag = (event, data) => {
    // unpack
    const { flipRatio, isDebug } = this.props
    const { deckElement, isVerso } = this.state
    isDebug && console.log('DEBUG: Deck - onDrag')
    // cursor
    const cursor = (event.clientY - this.state.clientY) / deckElement.offsetHeight
    if (
      (!isVerso && cursor < -flipRatio) ||
      (isVerso && cursor > flipRatio)
    ) {
      this.handleFlipCard()
    }
  }
  onNext = (event, diffIndex) => {
    this.props.isDebug && console.log('DEBUG: Deck - onNext')
    event.preventDefault()
    event.stopPropagation()
    this.handleNextItemCard(diffIndex)
  }
  onStop = (event, data) => {
    this.props.isDebug && console.log('DEBUG: Deck - onStop')
    this.setState({ isFlipping: false, y: null })
  }
  onResize = event => {
    this.props.isDebug && console.log('DEBUG Deck - onResize')
    this.setState({ isResizing: true })
  }
  onTransitionEndCard = (event, cardProps) => {
    // check and unpack
    const { transitions } = this
    const { handleTransitionEnd, isDebug } = this.props
    isDebug && console.log('DEBUG: Deck - onTransitionEndCard')
    // update the transitions store
    if (!transitions) {
      console.warn('transitions is null while we try to update transition end...? weird')
      return
    }
    const newTransitions = [...transitions]
    const transition = newTransitions[cardProps.index]
    if (transition && transition[event.propertyName]) {
        delete transition[event.propertyName]
        if (Object.keys(transition).length === 0) {
          newTransitions[cardProps.index] = false
        }
    }
    this.transitions = newTransitions
    // check
    if (newTransitions.every((newTransition, index) => !newTransition)) {
      handleTransitionEnd && handleTransitionEnd()
      this.setState({ isTransitioning: false })
      this.transitions = null
    }
  }
  onTransitionStartCard = (event, cardProps) => {
    // unpack
    const { transitions } = this
    const { contents,
      handleTransitionStart,
      isDebug
    } = this.props
    isDebug && console.log('DEBUG: Deck - onTransitionStartCard')
    // at the first time one of the card is transitioning
    // we init a new array
    let newTransitions
    if (!transitions) {
      newTransitions = [...new Array(contents.length)]
      this.setState({ isTransitioning: true })
      handleTransitionStart && handleTransitionStart()
    } else {
      newTransitions = [...transitions]
    }
    // for this particular card, maybe the transition
    // exists alreay or not
    if (!newTransitions[cardProps.index]) {
      newTransitions[cardProps.index] = { [event.propertyName]: true }
    } else {
      newTransitions[cardProps.index][event.propertyName] = true
    }
    this.transitions = newTransitions
  }
  componentWillMount() {
    this.handleResetItems(this.props)
  }
  componentWillReceiveProps (nextProps) {
    // unpack
    const { contents } = this.props
    const { isTransitioning } = this.state
    // look for content change
    if (nextProps.contents !== contents) {
      if (!isTransitioning) {
        nextProps.isDebug && console.log('DEBUG: Deck - componentWillReceiveProps')
        this.handleResetItems(nextProps)
        // init new state
        // transition to 'none' helps
        // the card to know that they should not remount with a style transition
        // because they are already at the good place
        this.setState({ transition: 'none' })
      }
    }
  }
  componentDidMount () {
    this.handleSetCurrentContent()
    this.setState({ deckElement: this.element })
    window.addEventListener('resize', this.onDebouncedResize)
  }
  componentDidUpdate (prevProps, prevState) {
    // unpack
    const { contents,
      isDebug,
      transitionTimeout
    } = this.props
    const { currentContent,
      transition,
      isResizing,
      items
    } = this.state
    // the deck updated because we changed the contents
    // so we need to wait just the refresh of the children
    // card to reset to false the transition
    if (transition === 'none') {
      this.setState({ transition: null })
    }
    // as the deck element has a dynamical width
    // we need to trigger again the set of the style
    // of the children when we resize the window
    if (isResizing && !prevState.isResizing) {
      this.setState({ isResizing: false })
    }
    isDebug && console.log('DEBUG: Deck - componentDidUpdate')
    // adapt the items and current content
    if (contents !== prevProps.contents || items !== prevState.items) {
      if (contents && !prevProps.contents) {
        isDebug && console.log('DEBUG: Deck - componentDidUpdate handleResetItems')
        this.handleResetItems()
      }
      isDebug && console.log('DEBUG: Deck - componentDidUpdate handleSetCurrentContent')
      this.handleSetCurrentContent()
    }
    // adapt style given current content
    if (transitionTimeout !== prevProps.transitionTimeout ||
      currentContent !== prevState.currentContent) {
      this.handleSetStyle()
    }
  }
  componentWillUnmount () {
    window.removeEventListener('resize', this.onDebouncedResize)
  }
  render () {
    const { handleFlipCard,
      handleNextItemCard,
      handleRelaxItemCard,
      handleSetCursorCard,
      handleSetTypeCard,
      handleSetReadCard,
      onDrag,
      onNext,
      onStart,
      onStop,
      onTransitionEndCard,
      onTransitionStartCard
    } = this
    const { contents,
      isLoadingBefore,
      isLoadingAfter,
      transitionTimeout,
      readTimeout
    } = this.props
    const { buttonStyle,
      currentContent,
      cursor,
      deckElement,
      gradientStyle,
      isFirstCard,
      isFlipping,
      isLastCard,
      isResizing,
      isTransitioning,
      isVerso,
      items,
      style,
      transition
    } = this.state
    const isAfterDisabled = !items || isLastCard || isTransitioning
    const isAfterHidden = currentContent && currentContent.isLast
    const isBeforeDisabled = !items || isFirstCard || isTransitioning
    const isBeforeHidden = currentContent && currentContent.isFirst
    const isFlipDisabled = !items || isTransitioning
    console.log('RENDER: Deck contents', contents && contents.length, contents,
    contents && contents.map(content => content && `${content.id} ${content.chosenOffer && content.chosenOffer.id} ${content.dateRead}`))
    // console.log('RENDER: Deck', 'this.state.items', this.state.items)
    // console.log(`RENDER: Deck isLoadingBefore ${isLoadingBefore} isLoadingAfter ${isLoadingAfter}`)
    return (
      <Draggable axis='y'
        bounds={{ bottom: 0, top: 0 }}
        onDrag={onDrag}
        onStart={onStart}
        onStop={onStop} >
        <div className='deck relative'
          id='deck'
          style={style}
          ref={element => this.element = element }>
          <button className={classnames('button deck__to-verso absolute right-0 mr2 top-0', {
            'button--hidden': !isVerso,
            'button--disabled': isTransitioning })}
            onClick={handleFlipCard} >
            X
          </button>
          {
            items && items.map((item, index) =>
              contents && contents[index] &&
              Math.abs(item) < 2 &&
                <Card content={contents && contents[index]}
                  contentLength={contents && contents.length}
                  cursor={cursor}
                  deckElement={deckElement}
                  handleFlipCard={handleFlipCard}
                  handleNextItem={handleNextItemCard}
                  handleRelaxItem={handleRelaxItemCard}
                  handleSetCursor={handleSetCursorCard}
                  handleSetRead={handleSetReadCard}
                  handleSetType={handleSetTypeCard}
                  isFirst={contents && !contents[index - 1]}
                  isFlipping={isFlipping}
                  isLast={contents && !contents[index + 1]}
                  index={index}
                  isResizing={isResizing}
                  isTransitioning={isTransitioning}
                  isVerso={isVerso}
                  item={item}
                  transition={transition}
                  transitionTimeout={transitionTimeout}
                  key={index}
                  onTransitionEnd={onTransitionEndCard}
                  onTransitionStart={onTransitionStartCard}
                  readTimeout={readTimeout} />
            )
          }
            <div className="deck-gradient" style={gradientStyle} />
            <div className='deck__board absolute'
              id='deck__board'
              ref={element => this.boardElement = element} >
              <div className='deck__board__control flex justify-around'>
                <button className={classnames('deck__board__before button', {
                  'button--disabled': isBeforeDisabled,
                  'button--hidden': isBeforeHidden })}
                  disabled={isBeforeDisabled}
                  onClick={event => onNext(event, 1)}
                  style={buttonStyle}>
                    <Icon svg='ico-prev-w' />
                </button>
                <button className={classnames('deck__board__to-recto button', {
                  'button--disabled': isFlipDisabled })}
                  onClick={handleFlipCard}
                  style={buttonStyle} >
                  <Icon svg='ico-slideup-w' />
                </button>
                <button className={classnames('deck__board__after button', {
                  'button--disabled': isAfterDisabled,
                  'button--hidden': isAfterHidden })}
                  onClick={event => onNext(event, -1)}
                  disabled={isAfterDisabled}
                  style={buttonStyle} >
                  <Icon svg='ico-prev-w' className='flip-horiz' />
                </button>
              </div>
              <button className='deck__board__profile'
                style={{ backgroundImage: "url('../icons/pc_small.jpg')" }} />
            </div>
          </div>
        </Draggable>
      )
    }
}

Deck.defaultProps = { deckKey: 0,
  flipRatio: 0.25,
  // isDebug: false,
  readTimeout: 3000,
  resizeTimeout: 250,
  transitionTimeout: 500
}

export default Deck
