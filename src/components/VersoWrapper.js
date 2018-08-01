import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import ControlBar from './ControlBar'
import currentHeaderColorSelector from '../selectors/currentHeaderColor'
import currentEventOrThingSelector from '../selectors/currentEventOrThing'
import currentVenueSelector from '../selectors/currentVenue'
import isCurrentTutoSelector from '../selectors/isCurrentTuto'
import { ROOT_PATH } from '../utils/config'

import { makeDraggable, makeUndraggable } from '../reducers/verso'

class VersoWrapper extends Component {
  componentDidUpdate(prevProps, prevState) {
    if (!this.props.isFlipped && prevProps.isFlipped) {
      this.element.scrollTo && this.element.scrollTo(0, 0)
    }
  }

  componentDidMount() {
    this.$el.addEventListener(
      'touchmove',
      e => {
        if (this.props.draggable && this.$el.scrollTop > 0) {
          this.props.makeUndraggable()
        } else if (!this.props.draggable && this.$el.scrollTop <= 0) {
          this.props.makeDraggable()
        }
      },
      { passive: true }
    )
  }

  componentWillUnMount() {
    this.$el.removeEventListener('touchmove')
  }

  render() {
    const {
      children,
      className,
      eventOrThing,
      hasControlBar,
      headerColor,
      isCurrentTuto,
      venue,
    } = this.props
    const contentStyle = {}
    if (isCurrentTuto) {
      contentStyle.backgroundColor = headerColor
    } else {
      contentStyle.backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
    }
    const author = get(eventOrThing, 'extraData.author')
    return (
      <div
        ref={$el => { this.$el = $el }}
        className={`verso-wrapper ${className || ''}`}>
        <div
          className="verso-header"
          style={{ backgroundColor: headerColor }}
          ref={element => (this.element = element)}>
          <h1>
            {' '}
            {eventOrThing && eventOrThing.name}
            {author && ', de ' + author}{' '}
          </h1>
          <h2> {venue && venue.name} </h2>
        </div>
        {hasControlBar && <ControlBar />}
        <div className="verso-content" style={{ ...contentStyle }}>
          {children}
        </div>
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { mediationId, offerId } = ownProps.match.params
      return {
        headerColor: currentHeaderColorSelector(state, offerId, mediationId),
        isFlipped: state.verso.isFlipped,
        draggable: state.verso.draggable,
        isCurrentTuto: isCurrentTutoSelector(state),
        eventOrThing: currentEventOrThingSelector(state, offerId, mediationId),
        venue: currentVenueSelector(state, offerId, mediationId),
      }
    },
    { makeDraggable, makeUndraggable }
  )
)(VersoWrapper)
