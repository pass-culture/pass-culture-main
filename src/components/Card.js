import classnames from 'classnames'
import Draggable from 'react-draggable'
import React, { Component } from 'react'

import Recto from './Recto'

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
    const { onDrag } = this.props
    // hook
    onDrag && onDrag(event, data)
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
    const { x } = data
    const newState = { position: { x: 0, y: 0 } }
    // thresholds
    const leftThreshold = - 0.1 * deckElement.offsetWidth
    const rightThreshold = 0.1 * deckElement.offsetWidth
    if (!isLast && x < leftThreshold) {
      onNext(-1)
      newState.transform = `perspective( ${perspective}px ) rotateY( ${rotation}deg )`
    } else if (!isFirst && x > rightThreshold) {
      onNext(1)
      newState.transform = `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
    } else {
      newState.transform = ''
    }
    // return
    this.setState(newState)
  }
  handleSetType = props => {
    const { contentLength, handLength, item } = props
    this.type = null
    if (item === 0) {
      this.type = 'current'
    } else if (item < 0) {
      if (item >= - handLength) {
        this.type = 'hand-left'
      } else {
        this.type = 'aside-left'
      }
    } else if (item <= handLength) {
      this.type = 'hand-right'
    } else {
      this.type = 'aside-right'
    }
  }
  handleSetStyle = props => {
    // unpack and check
    const { type } = this
    const { cursor,
      deckElement,
      item,
      perspective,
      rotation,
      handLength,
      widthRatio
    } = props
    if (!deckElement) {
      return
    }
    // compute the size of the container
    const halfWidth = 0.5 * deckElement.offsetWidth
    const leftOrRightWidth = halfWidth * (1 - widthRatio)
    const handWidth = leftOrRightWidth / handLength
    // determine style and transform given the type of the card
    let style = {}
    let transform
    switch (type) {
      case 'aside-left':
        style = { left: -100 }
        break
      case 'hand-left':
        style = {
          left: leftOrRightWidth - 0.1*halfWidth + (item + 1) * handWidth,
          width: handWidth
        }
        transform = `perspective( ${perspective}px ) rotateY( ${rotation}deg )`
        break
      case 'current':
        style = {
          left: leftOrRightWidth,
          right: leftOrRightWidth
        }
        transform = `perspective( ${perspective}px ) rotateY( ${-cursor*45}deg )`
        break
      case 'hand-right':
        style = {
          right: leftOrRightWidth - 0.1*halfWidth - (item - 1) * handWidth,
          width: handWidth
        }
        transform = `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
        break
      case 'aside-right':
        style = { right: 100 }
      default:
        return
    }
    this.setState({ style, transform })
  }
  handleCheckRead = props => {
    // unpack and check
    const { content,
      index,
      onRead,
      readTimeout
    } = props
    if (!content || this.type === 'current') { return }
    // wait a bit to trigger the fact that we stay on the same card
    setTimeout(() => {
      // check that type is still current
      this.type === 'current' && onRead && onRead(props)
    }, readTimeout)
  }
  componentWillMount () {
    this.handleSetType(this.props)
    this.handleSetStyle(this.props)
    this.handleCheckRead(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if ( (nextProps.deckElement && !this.props.deckElement)
      || (nextProps.item !== this.props.item)
      || (nextProps.cursor !== this.props.cursor)
      || (nextProps.content !== this.props.content)
    ) {
      this.handleSetType(nextProps)
      this.handleSetStyle(nextProps)
      this.handleCheckRead(nextProps)
    }
  }
  render () {
    const { type, onDrag, onStop } = this
    const { content,
      handLength,
      index,
      item
    } = this.props
    const { position,
      style,
      transform
    } = this.state
    return (
      <Draggable axis='x'
        disabled={type !== 'current'}
        position={position}
        onDrag={onDrag}
        onStop={onStop} >
          <span className={classnames('card absolute', {
            'card--current': type === 'current',
            'card--hidden': !content || Object.keys(content).length === 0
          })} style={style}>
            <div className='card__container' style={{ transform }}>
              <Recto {...content} />
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
