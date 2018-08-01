import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import ControlBar from './ControlBar'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import { ROOT_PATH } from '../utils/config'

import { makeDraggable, makeUndraggable } from '../reducers/verso'

class VersoWrapper extends Component {
  componentDidUpdate(prevProps, prevState) {
    if (!this.props.isFlipped && prevProps.isFlipped) {
      this.$header.scrollTo && this.$header.scrollTo(0, 0)
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
      currentRecommendation,
      headerColor,
    } = this.props
    const {
      mediation,
      offer
    } = (currentRecommendation || {})
    const {
      eventOrThing,
      venue
    } = (offer || {})
    const {
      tutoIndex
    } = (mediation || {})

    const contentStyle = {}
    if (typeof tutoIndex === 'number') {
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
          ref={$el => { this.$header = $el }}>
          <h1>
            {' '}
            {get(eventOrThing, 'name')}
            {author && ', de ' + author}{' '}
          </h1>
          <h2> {get(venue, 'name')} </h2>
        </div>
        {typeof tutoIndex !== 'number' && <ControlBar />}
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
        currentRecommendation: currentRecommendationSelector(state, offerId, mediationId),
        isFlipped: state.verso.isFlipped,
        draggable: state.verso.draggable
      }
    },
    { makeDraggable, makeUndraggable }
  )
)(VersoWrapper)
