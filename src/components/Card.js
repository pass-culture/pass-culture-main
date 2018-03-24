import classnames from 'classnames'
import React, { Component } from 'react'
import Draggable from 'react-draggable'
import { Portal } from 'react-portal'

import Clue from './Clue'
import Recto from './Recto'
import Verso from './Verso'

export const CURRENT = 'current'
export const ASIDE_LEFT = 'aside-left'
export const ASIDE_RIGHT = 'aside-right'
export const HAND_LEFT = 'hand-left'
export const HAND_RIGHT = 'hand-right'

class Card extends Component {
  constructor () {
    super()
    this.state = { cursor: null,
      item: null,
      isRead: false,
      position: null,
      transform: null,
      style: null
    }
  }
  handleSetRead = props => {
    // unpack and check
    const { content,
      handleSetRead,
      readTimeout
    } = props
    const { isRead } = this.state
    if (!content || isRead) { return }
    // wait a bit to trigger the fact that we stay on the same card
    this.readTimeout = setTimeout(() => {
      // make sure we are not going to do it circularly
      this.setState({ isRead: true })
      // check that type is still current
      this.state.type === CURRENT && handleSetRead && handleSetRead(props)
    }, readTimeout)
  }
  handleSetType = props => {
    // unpack and check
    const { cursor,
      deckElement,
      handleSetType,
      isSetRead,
      onTransitionStart,
      transition,
      transitionTimeout
    } = props
    const item = this.state.item || props.item
    if (!deckElement) {
      return
    }
    // determine the type of the card
    let type
    if (item === 0) {
      type = CURRENT
    } else if (item < 0) {
      if (item >= - 2) {
        type = HAND_LEFT
      } else {
        type = ASIDE_LEFT
      }
    } else if (item <= 2) {
      type = HAND_RIGHT
    } else {
      type = ASIDE_RIGHT
    }
    // determine style and transform given the type of the card
    let style, transform
    switch (type) {
      case ASIDE_LEFT:
        style = {
          left: - deckElement.offsetWidth,
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: deckElement.offsetWidth
        }
        break
      case HAND_LEFT:
        style = {
          left: - (1 - cursor) * deckElement.offsetWidth,
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: deckElement.offsetWidth
        }
        break
      case CURRENT:
        style = {
          left: 0,
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: deckElement.offsetWidth
        }
        break
      case HAND_RIGHT:
        style = {
          left: deckElement.offsetWidth + cursor * deckElement.offsetWidth,
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: deckElement.offsetWidth
        }
        break
      case ASIDE_RIGHT:
        style = {
          left: 2 * deckElement.offsetWidth,
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: deckElement.offsetWidth
        }
        break
      default:
        break
    }
    // check read
    isSetRead && type === CURRENT && this.handleSetRead(props)
    // transition happened when the style has been already set once
    // and that the new style has a not none transform
    if (this.state.style && style.transition !== 'none') {
      onTransitionStart && Object.keys(style)
       .filter(key => !/transition(.*)/.test(key))
       .forEach(key => {
          if (style[key] !== this.state.style[key]) {
            onTransitionStart({ propertyName: key }, this.props)
          }
        })
    }
    // inform parent about the new current card
    const newState = { isRead: false,
      style,
      transform,
      type
    }
    // update
    this.setState(newState)
    // hook
    handleSetType && handleSetType(props, newState)
  }
  onDrag = (event, data) => {
    // unpack
    const { deckElement,
      handleSetCursor
    } = this.props
    const { x } = data
    // compute the cursor
    const cursor = x / deckElement.offsetWidth
    // hook
    handleSetCursor && handleSetCursor(cursor)
  }
  onTransitionEnd = event => {
    const { onTransitionEnd } = this.props
    onTransitionEnd && onTransitionEnd(event, this.props)
  }
  onStop = (event, data) => {
    // unpack
    const { deckElement,
      handleNextItem,
      handleRelaxItem,
      isFirst,
      isLast
    } = this.props
    const { x } = data
    // special reset for the CURRENT CARD
    // we need to clear the position given by x and y
    // and transfer the position state into the style state one
    this.setState({
      position: { x:0, y:0 },
      style: Object.assign({}, this.state.style, { left: x })
    })
    // thresholds
    const leftThreshold = - 0.1 * deckElement.offsetWidth
    const rightThreshold = 0.1 * deckElement.offsetWidth
    if (!isLast && x < leftThreshold) {
      handleNextItem(-1)
    } else if (!isFirst && x > rightThreshold) {
      handleNextItem(1)
    } else {
      handleRelaxItem && handleRelaxItem(data)
    }
  }
  componentDidMount () {
    this.onTransitionEndListener = this.cardElement.addEventListener(
      'transitionend',
      this.onTransitionEnd
    )
  }
  componentWillMount () {
    this.handleSetType(this.props)
  }
  componentWillReceiveProps (nextProps, nextState) {
    const { cursor,
      deckElement,
      isResizing,
      item
    } = nextProps
    if ( (deckElement && !this.props.deckElement)
      || (item !== this.props.item)
      || (isResizing && !this.props.isResizing)
      || (cursor !== this.props.cursor && item > - 2 && item < 2)
    ) {
      this.handleSetType(nextProps)
    }
  }
  componentWillUnmount () {
    this.cardElement.removeEventListener('transitionend', this.onTransitionEnd)
    this.readTimeout && clearTimeout(this.readTimeout)
  }
  render () {
    const { onDrag,
      onStop
    } = this
    const {
      content,
      contentLength,
      deckElement,
      handleFlipCard,
      index,
      isFirst,
      isFlipping,
      isLast,
      isTransitioning,
      isVerso,
      item,
      transitionTimeout
    } = this.props
    const { position,
      style,
      transform,
      type
    } = this.state
    const isDraggable = type === 'current' &&
      !isTransitioning &&
      !isVerso &&
      !isFlipping
    const bounds = {}
    if (isFirst) {
      bounds.right = 0
    } else if (isLast) {
      bounds.left = 0
    }
    return (
      [
        <Draggable axis='x'
          bounds={bounds}
          disabled={!isDraggable}
          key={0}
          position={position}
          onDrag={onDrag}
          onStop={onStop} >
            <span className={classnames('card absolute', {
                'card--current': type === CURRENT,
                'card--draggable': isDraggable
              })}
              ref={element => this.cardElement = element}
              style={style}>
              <div className='card__container' style={{ transform }}>
                <Recto {...content}
                  contentLength={contentLength}
                  index={index}
                  item={item} />
              </div>
            </span>
        </Draggable>,
        item === 0 && (
          <Portal key={1} node={document && document.getElementById('deck')}>
            <Verso {...content}
              deckElement={deckElement}
              handleFlipCard={handleFlipCard}
              isFlipped={isVerso} />
          </Portal>
        ),
        item > -2 && item < 2 && (
          <Portal key={2} node={document && document.getElementById('deck__board')}>
            <Clue {...content}
              contentLength={contentLength}
              index={index}
              item={item}
              transitionTimeout={transitionTimeout} />
          </Portal>
        )
      ]
    )
  }
}

Card.defaultProps = { isSetRead: true,
  readTimeout: 3000,
  transitionDelay: 100,
  transitionTimeout: 250
}

export default Card
