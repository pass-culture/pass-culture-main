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
    this.state = { position: null,
      transform: null,
      style: null
    }
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
  onStop = (event, data) => {
    // unpack
    const { deckElement,
      isFirst,
      isLast,
      item,
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
      console.log('ICI')
      newState.transform = `perspective( ${perspective}px ) rotateY( 0deg )`
    }
    // return
    this.setState(newState)
  }
  handleSetStyle = props => {
    // unpack and check
    const { contentLength,
      deckElement,
      perspective,
      rotation,
      handLength,
      widthRatio
    } = props
    // cursor is defined in state if it is the current card
    // or possibly in props given by the deck parent component
    const cursor = this.state.cursor || props.cursor
    const item = this.item || props.item
    if (!deckElement) {
      return
    }
    // determine the type of the card
    let type
    if (item === 0) {
      type = 'current'
    } else if (item < 0) {
      if (item >= - handLength) {
        type = 'hand-left'
      } else {
        type = 'aside-left'
      }
    } else if (item <= handLength) {
      type = 'hand-right'
    } else {
      type = 'aside-right'
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
      // right: leftOrRightCurrentWidth,
      width: currentWidth
    }
    transformsByType[CURRENT] = `perspective( ${perspective}px ) rotateY( ${-cursor * rotation}deg )`
    // hand right
    stylesByType[HAND_RIGHT] = {
      left: deckElement.offsetWidth - leftOrRightCurrentWidth + (item - 1) * handWidth,
      // right: leftOrRightCurrentWidth - 0.1 * halfWidth - (item - 1) * handWidth,
      width: handWidth
    }
    transformsByType[HAND_RIGHT] = `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
    // aside right
    stylesByType[ASIDE_RIGHT] = {
      left: deckElement.offsetWidth + 100,
      // right: -100,
      width: handWidth
    }
    transformsByType[ASIDE_RIGHT] = `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
    // update
    const style = stylesByType[type]
    const transform = transformsByType[type]
    this.setState({ style,
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
    const { type } = this.state
    if (!content || type !== CURRENT) { return }
    // wait a bit to trigger the fact that we stay on the same card
    setTimeout(() => {
      // check that type is still current
      this.state.type === CURRENT && onRead && onRead(props)
    }, readTimeout)
  }
  componentWillMount () {
    this.handleSetStyle(this.props)
    this.handleCheckRead(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if ( (nextProps.deckElement && !this.props.deckElement)
      || (nextProps.item !== this.props.item)
      || (nextProps.cursor !== this.props.cursor)
      || (nextProps.content !== this.props.content)
    ) {
      this.handleSetStyle(nextProps)
      this.handleCheckRead(nextProps)
    }
  }
  render () {
    const { onDrag, onStop } = this
    const { content,
      contentLength,
      handLength,
      index,
      item
    } = this.props
    const { position,
      style,
      transform,
      type
    } = this.state
    console.log('item', item, content, type)
    return (
      <Draggable axis='x'
        disabled={type !== 'current'}
        position={position}
        onDrag={onDrag}
        onStop={onStop} >
          <span className={classnames('card absolute', {
            'card--current': type === CURRENT
          })} style={style}>
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

Card.defaultProps = {
  perspective: 600,
  readTimeout: 3000,
  rotation: 45,
  widthRatio: 0.75
}

export default Card
