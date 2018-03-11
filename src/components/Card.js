import classnames from 'classnames'
import Draggable from 'react-draggable'
import React, { Component } from 'react'

import Recto from './Recto'

const CURRENT = 'current'
const ASIDE_LEFT = 'aside-left'
const ASIDE_RIGHT = 'aside-right'
const HAND_LEFT = 'hand-left'
const HAND_RIGHT = 'hand-right'

class Card extends Component {
  constructor () {
    super()
    this.state = { cursor: null,
      item: null,
      isRead: false,
      isTransitioning: false,
      position: null,
      transform: null,
      style: null
    }
  }
  handleSetStyle = props => {
    // unpack and check
    const { contentLength,
      deckElement,
      handLength,
      isCheckRead,
      isContentChanging,
      onTransitionStart,
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
    const halfWidth = 0.5 * deckElement.offsetWidth
    const leftOrRightCurrentWidth = halfWidth * (1 - widthRatio)
    const currentWidth = deckElement.offsetWidth - 2 * leftOrRightCurrentWidth
    const handWidth = leftOrRightCurrentWidth / handLength
    // determine style and transform given the type of the card
    const stylesByType = {}
    const transformsByType = {}
    // aside left
    stylesByType[ASIDE_LEFT] = {
      left: -100,
      width: handWidth
    }
    transformsByType[ASIDE_LEFT] = `perspective( ${perspective}px ) rotateY( ${rotation}deg )`
    // hand left
    stylesByType[HAND_LEFT] = {
      left: leftOrRightCurrentWidth + item * handWidth,
      width: handWidth
    }
    transformsByType[HAND_LEFT] = `perspective( ${perspective}px ) rotateY( ${rotation}deg )`
    // current
    stylesByType[CURRENT] = {
      left: leftOrRightCurrentWidth,
      width: currentWidth
    }
    transformsByType[CURRENT] = `perspective( ${perspective}px ) rotateY( ${-cursor * rotation}deg )`
    // hand right
    stylesByType[HAND_RIGHT] = {
      left: deckElement.offsetWidth - leftOrRightCurrentWidth + (item - 1) * handWidth,
      width: handWidth
    }
    transformsByType[HAND_RIGHT] = `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
    // aside right
    stylesByType[ASIDE_RIGHT] = {
      left: deckElement.offsetWidth + 100,
      width: handWidth
    }
    transformsByType[ASIDE_RIGHT] = `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
    // set is transitioning
    this.handleSetIsTransitioning(props)
    // check read
    isCheckRead && type === CURRENT && this.handleCheckRead(props)
    // determine style
    const style = stylesByType[type]
    style.transition = isContentChanging
      ? 'none'
      : `left ${transitionTimeout}ms, width ${transitionTimeout}ms, transform 0s`
    const transform = transformsByType[type]
    // transition start
    style.transition !== 'none' &&
      this.state.style &&
      onTransitionStart &&
      Object.keys(style).forEach(key => {
      if (key !== 'transition' && style[key] !== this.state.style[key]) {
        // console.log(type, key, props.content.id, props.item, props.index)
        onTransitionStart({ propertyName: key }, this.props)
      }
    })
    // update
    this.setState({ isRead: false,
      style,
      stylesByType,
      transform,
      transformsByType,
      type
    })
  }
  handleCheckRead = props => {
    // unpack and check
    const { content,
      index,
      onRead,
      readTimeout
    } = props
    const { isRead } = this.state
    if (!content || isRead) { return }
    // wait a bit to trigger the fact that we stay on the same card
    setTimeout(() => {
      // make sure we are not going to do it circularly
      this.setState({ isRead: true })
      // check that type is still current
      this.state.type === CURRENT && onRead && onRead(props)
    }, readTimeout)
  }
  handleSetIsTransitioning = props => {
    const { isBlobModel, transitionTimeout } = props
    if (isBlobModel) {
      return
    }
    // we can here be sure that the user
    // will not swipe too fast...
    // takes the transition timeout to do animation + refresh of the extreme contents
    // This is possible by setting a isTransitioning disabling the dragging
    this.setState({ isTransitioning: true })
    setTimeout(() => this.setState({ isTransitioning: false }),
      transitionTimeout)
  }
  onDrag = (event, data) => {
    // unpack
    const { deckElement, onDrag } = this.props
    // compute the cursor
    const cursor = data.x / (deckElement.offsetWidth / 2)
    this.setState({ cursor })
    this.handleSetStyle(this.props)
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
      isFirst,
      isLast,
      onNext,
      perspective,
      rotation
    } = this.props
    const { stylesByType, transformsByType } = this.state
    const { x } = data
    const newState = {
      cursor: 0,
      position: { x: 0, y: 0 }
    }
    // thresholds
    const leftThreshold = - 0.1 * deckElement.offsetWidth
    const rightThreshold = 0.1 * deckElement.offsetWidth
    if (!isLast && x < leftThreshold) {
      onNext(-1)
    } else if (!isFirst && x > rightThreshold) {
      onNext(1)
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
    this.handleSetStyle(this.props)
  }
  componentWillReceiveProps (nextProps, nextState) {
    if ( (nextProps.deckElement && !this.props.deckElement)
      || (nextProps.item !== this.props.item)
      || (nextProps.cursor !== this.props.cursor)
    ) {
      // console.log('nextProps.item', nextProps.item, 'this.props.item', this.props.item)
      this.handleSetStyle(nextProps)
    }
  }
  componentWillUnmount () {
    this.cardElement.removeEventListener('transitionend',
      this.onTransitionEnd)
  }
  render () {
    const { onDrag,
      onStop,
      onTransitionEnd
    } = this
    const { content,
      contentLength,
      handLength,
      index,
      item
    } = this.props
    const { isTransitioning,
      position,
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
              'card--draggable': isDraggable
            })}
            ref={element => this.cardElement = element}
            style={style}
          >
            <div className='card__container' style={{ transform }}>
              <Recto {...content}
                contentLength={contentLength}
                index={index}
                item={item} />
            </div>
          </span>
      </Draggable>
    )
  }
}

Card.defaultProps = { isCheckRead: true,
  perspective: 600,
  readTimeout: 3000,
  rotation: 45,
  transitionTimeout: 500,
  widthRatio: 0.75
}

export default Card
