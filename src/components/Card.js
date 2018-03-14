import classnames from 'classnames'
import Draggable from 'react-draggable'
import React, { Component } from 'react'

import Recto from './Recto'

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
    setTimeout(() => {
      // make sure we are not going to do it circularly
      this.setState({ isRead: true })
      // check that type is still current
      this.state.type === CURRENT && handleSetRead && handleSetRead(props)
    }, readTimeout)
  }
  handleSetType = props => {
    // unpack and check
    const { deckElement,
      handLength,
      handleSetType,
      isSetRead,
      isContentChanging,
      isFullWidth,
      onTransitionStart,
      transition,
      transitionDelay,
      transitionTimeout,
      perspective,
      rotation,
      widthRatio
    } = props
    // cursor is defined in state if it is the current card
    // or possibly in props given by the deck parent component
    const cursor = this.state.cursor || props.cursor
    const item = this.state.item || props.item
    if (!deckElement) {
      return
    }
    // determine the type of the card
    let type
    if (item === 0) {
      type = CURRENT
    } else if (item < 0) {
      if (item >= - handLength) {
        type = HAND_LEFT
      } else {
        type = ASIDE_LEFT
      }
    } else if (item <= handLength) {
      type = HAND_RIGHT
    } else {
      type = ASIDE_RIGHT
    }
    // compute the size of the container
    let handWidth, leftOrRightCurrentWidth
    if (isFullWidth) {
      leftOrRightCurrentWidth = 0
      handWidth = handLength * deckElement.offsetWidth
    } else {
      const halfWidth = 0.5 * deckElement.offsetWidth
      leftOrRightCurrentWidth = halfWidth * (1 - widthRatio)
      handWidth = leftOrRightCurrentWidth / handLength
    }
    const currentWidth = deckElement.offsetWidth - 2 * leftOrRightCurrentWidth
    // determine style and transform given the type of the card
    let style, transform
    switch (type) {
      case ASIDE_LEFT:
        style = {
          left: - (isFullWidth ? currentWidth : handWidth),
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: isFullWidth ? currentWidth : handWidth
        }
        transform = !isFullWidth && `perspective( ${perspective}px ) rotateY( ${rotation}deg )`
        break
      case HAND_LEFT:
        style = {
          left: leftOrRightCurrentWidth + (isFullWidth ? - currentWidth : item * handWidth),
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: isFullWidth ? currentWidth : handWidth
        }
        transform = !isFullWidth && `perspective( ${perspective}px ) rotateY( ${rotation}deg )`
        break
      case CURRENT:
        style = {
          left: leftOrRightCurrentWidth,
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: currentWidth
        }
        transform = !isFullWidth && `perspective( ${perspective}px ) rotateY( ${-cursor * rotation}deg )`
        break
      case HAND_RIGHT:
        style = {
          left: deckElement.offsetWidth - leftOrRightCurrentWidth + (isFullWidth ? 0 : (item - 1) * handWidth),
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: isFullWidth ? currentWidth : handWidth
        }
        transform = !isFullWidth && `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
        break
      case ASIDE_RIGHT:
        style = {
          left: deckElement.offsetWidth + (isFullWidth ? currentWidth : handWidth),
          transition: transition ||
            `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`,
          width: isFullWidth ? currentWidth : handWidth
        }
        transform = !isFullWidth && `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
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
            // console.log(type, key, props.content.id, props.item, props.index)
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
    const { deckElement, onDrag } = this.props
    // compute the cursor
    const cursor = data.x / (deckElement.offsetWidth / 2)
    this.setState({ cursor })
    this.handleSetType(this.props)
    // hook
    onDrag && onDrag(event, data)
  }
  onTransitionEnd = event => {
    const { onTransitionEnd } = this.props
    onTransitionEnd && onTransitionEnd(event, this.props)
  }
  onStop = (event, data) => {
    // unpack
    const { deckElement,
      handleNextItem,
      isFirst,
      isLast,
      perspective
    } = this.props
    const { x } = data
    const newState = {
      cursor: 0,
      position: { x: 0, y: 0 }
    }
    // thresholds
    const leftThreshold = - 0.1 * deckElement.offsetWidth
    const rightThreshold = 0.1 * deckElement.offsetWidth
    if (!isLast && x < leftThreshold) {
      handleNextItem(-1)
    } else if (!isFirst && x > rightThreshold) {
      handleNextItem(1)
    } else {
      newState.transform = `perspective( ${perspective}px ) rotateY( 0deg )`
    }
    // return
    this.setState(newState)
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
    ) {
      // console.log('nextProps.item', nextProps.item, 'this.props.item', this.props.item)
      this.handleSetType(nextProps)
    }
    /*
    console.log(cursor)
    if ((item === - 1 || item === 1) && cursor !== this.props.cursor) {
      console.log('OUUUAAA')
    }
    */
  }
  componentWillUnmount () {
    this.cardElement.removeEventListener('transitionend',
      this.onTransitionEnd)
  }
  render () {
    const { onDrag,
      onStop
    } = this
    const { content,
      contentLength,
      index,
      isFullWidth,
      isTransitioning,
      item
    } = this.props
    const { position,
      style,
      transform,
      type
    } = this.state
    const isDraggable = type === 'current' && !isTransitioning
    return (
      <Draggable axis='x'
        disabled={!isDraggable}
        position={position}
        onDrag={onDrag}
        onStop={onStop} >
          <span className={classnames('card absolute', {
              'card--current': type === CURRENT,
              'card--draggable': isDraggable,
              'card--small': !isFullWidth
            })}
            ref={element => this.cardElement = element}
            style={style}
          >
            <div className={classnames('card__container', {
              'card__container--small': !isFullWidth
            })} style={{ transform }}>
              <Recto {...content}
                contentLength={contentLength}
                index={index}
                item={item}
                isFullWidth={isFullWidth} />
            </div>
          </span>
      </Draggable>
    )
  }
}

Card.defaultProps = { isSetRead: true,
  perspective: 600,
  readTimeout: 3000,
  rotation: 45,
  transitionDelay: 100,
  transitionTimeout: 500,
  widthRatio: 0.75
}

export default Card
