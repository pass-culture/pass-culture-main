import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Card from './Card'

class Deck extends Component {
  constructor () {
    super()
    this.state = { cursor: 0,
      deckElement: null,
      items: null
    }
  }
  handleIndexes = props => {
    const { size } = props
    this.setState({ items: [...Array(2* size + 3).keys()] })
  }
  onDragCard = (event, data) => {
    this.setState({ cursor: data.x / (this._element.offsetWidth / 2) })
  }
  onNextCard = diffIndex => {
    const { items } = this.state
    this.setState({ cursor: 0,
      items: items.map(index => index + diffIndex)
    })
  }
  componentWillMount () {
    this.handleIndexes(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.size !== this.props.size) {
      this.handleIndexes(nextProps)
    }
  }
  componentDidMount () {
    this.setState({ deckElement: this._element })
  }
  render () {
    const { size } = this.props
    const { cursor, deckElement, items } = this.state
    console.log('items', items)
    return (
      <div className='deck relative m3'
        ref={_element => this._element = _element }>
        {
          items.map((item, index) =>
            <Card cursor={cursor}
              deckElement={deckElement}
              index={index}
              item={item}
              key={index}
              onDrag={this.onDragCard}
              onNext={this.onNextCard}
              size={size} />
          )
        }
      </div>
    )
  }
}

Deck.defaultProps = {
  size: 2
}

export default Deck
