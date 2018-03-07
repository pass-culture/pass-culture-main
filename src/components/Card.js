import classnames from 'classnames'
import Draggable from 'react-draggable'
import React, { Component } from 'react'

import Recto from './Recto'

class Card extends Component {
  constructor () {
    super()
    this.state = { isCenter: false,
      position: null,
      style: null
    }
  }
  onDrag = (event, data) => {
    // unpack
    const { isCenter, onDrag } = this.props
    // hook with the Deck on Drag method
    isCenter && onDrag(event, data)
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
    const { style } = this.state
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
  handleStyle = props => {
    const { cursor,
      deckElement,
      item,
      perspective,
      rotation,
      size,
      widthRatio
    } = props
    if (!deckElement) {
      return
    }
    const halfWidth = 0.5 * deckElement.offsetWidth
    const leftOrRightWidth = halfWidth * (1 - widthRatio)
    const asideWidth = leftOrRightWidth/size
    let style = {}
    let transform
    if (item < 1) {
      style = { left: '-100%' }
    } else if (item < size + 1) {
      style = {
        left: (item - 1) * asideWidth,
        width: asideWidth
      }
      transform = `perspective( ${perspective}px ) rotateY( ${rotation}deg )`
    } else if (item === size + 1) {
      style = {
        left: leftOrRightWidth,
        right: leftOrRightWidth
      }
      transform = `perspective( ${perspective}px ) rotateY( ${-cursor*45}deg )`
    } else if (item < 2 * size + 2) {
      style = {
        right: `${(2 * size + 1 - item) * asideWidth}px`,
        width: asideWidth
      }
      transform = `perspective( ${perspective}px ) rotateY( -${rotation}deg )`
    } else {
      style = { right: '-100%' }
    }
    this.setState({ style, transform })
  }
  handleRead = props => {
    const { index,
      onRead,
      readTimeout
    } = props
    setTimeout(() => {
      onRead && onRead(props)
    }, readTimeout)
  }
  componentWillMount () {
    this.handleStyle(this.props)
    if (this.props.content && this.props.isCenter) {
      this.handleRead(this.props)
    }
  }
  componentWillReceiveProps (nextProps) {
    if ( (nextProps.deckElement && !this.props.deckElement)
      || (nextProps.item !== this.props.item)
      || (nextProps.cursor !== this.props.cursor)
    ) {
      this.handleStyle(nextProps)
    }
    if (
      (nextProps.isCenter && nextProps.content) &&
      (!this.props.content || !this.props.isCenter)
    ) {
      this.handleRead(nextProps)
    }
  }
  render () {
    const { onDrag, onStop } = this
    const { content,
      index,
      isCenter,
      item,
      size
    } = this.props
    const { position,
      style,
      transform
    } = this.state
    return (
      <Draggable axis='x'
        disabled={!isCenter}
        position={position}
        {...isCenter && {
          onDrag,
          onStop
        }}>
          <span className={classnames('card absolute', {
            'card--center': isCenter,
            'card--hidden': !content
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
