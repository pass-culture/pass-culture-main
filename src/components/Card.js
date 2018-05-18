import classnames from 'classnames'
import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import withSizes from 'react-sizes'

import Recto from './Recto'
import Verso from './Verso'
import selectCurrentHeaderColor from '../selectors/currentHeaderColor'
import { compose } from 'redux'

class Card extends Component {
  handleSetRead = props => {
    // unpack and check
    const { content, handleSetRead, item, readTimeout } = props
    const { isRead } = this.state
    if (!content || isRead) {
      return
    }
    // wait a bit to trigger the fact that we stay on the same card
    this.readTimeout = setTimeout(() => {
      // make sure we are not going to do it circularly
      this.setState({ isRead: true })
      // check that style is still current
      item === 0 && handleSetRead && handleSetRead(props)
    }, readTimeout)
  }

  componentWillUnmount() {
    this.readTimeout && clearTimeout(this.readTimeout)
  }

  render() {
    const { recommendation, position, currentHeaderColor, width } = this.props
    return (
      <div
        className={classnames('card', {
          current: position === 'current',
        })}
        style={{
          transform: `translate(${get(recommendation, 'index') * width}px, 0)`,
          backgroundColor: currentHeaderColor,
        }}
      >
        <Recto {...recommendation} />
        {position === 'current' && <Verso />}
      </div>
    )
  }
}

Card.defaultProps = {
  isSetRead: true,
  readTimeout: 3000,
}

export default compose(
  withSizes(({ width, height }) => ({
    width: Math.min(width, 500), // body{max-width: 500px;}
    height,
  })),
  connect(
    state => ({
      currentHeaderColor: selectCurrentHeaderColor(state),
      isFlipped: state.verso.isFlipped,
    }))
)(Card)
