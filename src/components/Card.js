import classnames from 'classnames'
import Draggable from 'react-draggable'
import React, { Component } from 'react'

class Card extends Component {
  constructor () {
    super()
    this.state = { position: null, style: null }
  }
  onDrag = (event, data) => {
    const { deckElement, onDrag } = this.props
    const { x, y } = data
    console.log('x, y, deckElement.width', x,y, deckElement && deckElement.offsetWidth)
    onDrag(event, data)
  }
  onStop = (event, data) => {
    const { deckElement, onNext } = this.props
    const { x } = data
    const leftThreshold = - 0.1 * deckElement.offsetWidth
    const rightThreshold = 0.1 * deckElement.offsetWidth
    if (x < leftThreshold) {
      console.log('X')
      onNext(-1)
      this.setState({ position: null })
    } else if (x > rightThreshold) {
      console.log('Y')
      onNext(1)
      this.setState({ position: null })
    } else {
      this.setState({ position: { x: 0, y: 0 } })
    }
  }
  handleStyle = props => {
    const { cursor,
      deckElement,
      item,
      size,
      widthRatio
    } = props
    if (!deckElement) {
      return
    }
    console.log('cursor', cursor)
    const halfWidth = 0.5 * deckElement.offsetWidth
    const leftOrRightWidth = halfWidth * (1 - widthRatio)
    const asideWidth = leftOrRightWidth/size
    let style = {}
    if (item < 1) {
      style = { left: '-100%' }
    } else if (item < size + 1) {
      style = {
        left: (item - 1) * asideWidth,
        transform: 'perspective( 600px ) rotateY( 45deg )',
        width: asideWidth
      }
    } else if (item === size + 1) {
      style = {
        left: leftOrRightWidth,
        right: leftOrRightWidth,
        transform: 'perspective( 600px ) rotateY( 45deg )',
      }
    } else if (item < 2 * size + 2) {
      style = {
        right: `${(2 * size + 1 - item) * asideWidth}px`,
        transform: 'perspective( 600px ) rotateY( -45deg )',
        width: asideWidth
      }
    } else {
      style = { right: '-100%' }
    }
    // console.log(item, 'style', style)
    this.setState({ style })
  }
  componentWillMount () {
    this.handleStyle(this.props)
  }
  componentWillReceiveProps (nextProps) {
    // console.log(nextProps.item)
    if ( (nextProps.deckElement && !this.props.deckElement)
      || (nextProps.item !== this.props.item)
      || (nextProps.cursor !== this.props.cursor)
    ) {
      this.handleStyle(nextProps)
    }
    // console.log('OK')
  }
  render () {
    const { index,
      item,
      size
    } = this.props
    const { position, style } = this.state
    const isCenter = item === size + 1
    const cardElement = (
      <div className={classnames('card absolute', {
        'card--center': isCenter,
        'card--aside': !isCenter
      })} style={style} >
        {index}
      </div>
    )
    if (!isCenter) {
      return cardElement
    }
    return (
      <Draggable axis='x'
        position={position}
        onDrag={this.onDrag}
        onStop={this.onStop}>
          {cardElement}
      </Draggable>
    )
  }
}


Card.defaultProps = {
  widthRatio: 0.75
}
export default Card
