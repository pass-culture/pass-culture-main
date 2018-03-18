import classnames from 'classnames'
import React, { Component } from 'react'

class Verso extends Component {
  render () {
    const { deckElement, isFlipped } = this.props
    return (
      <div className={classnames('verso absolute', {
        'verso--flipped': isFlipped
      })}>
        QSDSQD
      </div>
    )
  }
}

export default Verso
