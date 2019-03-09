/* eslint
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoControl from './VersoControl'
import { getHeaderColor } from '../../utils/colors'
import currentRecommendationSelector from '../../selectors/currentRecommendation'
import { ROOT_PATH } from '../../utils/config'

import { makeDraggable, makeUndraggable } from '../../reducers/card'

export class RawVersoWrapper extends Component {
  constructor(props) {
    super(props)
    this.toucheMoveHandler = this.toucheMoveHandler.bind(this)
  }

  componentDidMount() {
    if (!this.$el) return
    const opts = { passive: true }
    this.$el.addEventListener('touchmove', this.toucheMoveHandler, opts)
  }

  componentDidUpdate(prevProps) {
    const { areDetailsVisible } = this.props
    const shouldScroll =
      !areDetailsVisible && prevProps.areDetailsVisible && this.$header.scrollTo
    if (!shouldScroll) return
    this.$header.scrollTo(0, 0)
  }

  componentWillUnmount() {
    if (!this.$el) return
    this.$el.removeEventListener('touchmove', this.toucheMoveHandler)
  }

  toucheMoveHandler() {
    const {
      draggable,
      dispatchMakeUndraggable,
      dispatchMakeDraggable,
    } = this.props
    if (draggable && this.$el.scrollTop > 0) {
      dispatchMakeUndraggable()
    } else if (!draggable && this.$el.scrollTop <= 0) {
      dispatchMakeDraggable()
    }
  }

  render() {
    const { children, className, currentRecommendation } = this.props

    const firstThumbDominantColor = get(
      currentRecommendation,
      'firstThumbDominantColor'
    )
    const headerColor = getHeaderColor(firstThumbDominantColor)

    const { mediation, offer } = currentRecommendation || {}
    const { eventOrThing, venue } = offer || {}

    const { tutoIndex } = mediation || {}

    const contentStyle = {}
    contentStyle.backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
    if (typeof tutoIndex === 'number') {
      contentStyle.backgroundColor = headerColor
    }

    const offerVenue = get(venue, 'name')
    const author = get(eventOrThing, 'extraData.author')
    let offerName = get(eventOrThing, 'name')
    if (author) offerName = `${offerName}, de ${author}`
    return (
      <div
        ref={$el => {
          this.$el = $el
        }}
        className={`verso-wrapper ${className || ''}`}
      >
        <div
          className="verso-header"
          style={{ backgroundColor: headerColor }}
          ref={$el => {
            this.$header = $el
          }}
        >
          <h1
            id="verso-offer-name"
            style={{ lineHeight: '2.7rem' }}
            className="fs40 is-medium is-hyphens"
          >
            {offerName}
          </h1>
          <h2 id="verso-offer-venue" className="fs22 is-normal is-hyphens">
            {offerVenue}
          </h2>
        </div>
        {typeof tutoIndex !== 'number' && <VersoControl />}
        <div className="verso-content" style={{ ...contentStyle }}>
          {children}
        </div>
      </div>
    )
  }
}

RawVersoWrapper.defaultProps = {
  currentRecommendation: null,
}

RawVersoWrapper.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  children: PropTypes.node.isRequired,
  className: PropTypes.string.isRequired,
  currentRecommendation: PropTypes.object,
  dispatchMakeDraggable: PropTypes.func.isRequired,
  dispatchMakeUndraggable: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { mediationId, offerId } = ownProps.match.params
      const currentRecommendation = currentRecommendationSelector(
        state,
        offerId,
        mediationId
      )
      return {
        areDetailsVisible: state.card.areDetailsVisible,
        currentRecommendation,
        draggable: state.card.draggable,
      }
    },
    {
      dispatchMakeDraggable: makeDraggable,
      dispatchMakeUndraggable: makeUndraggable,
    }
  )
)(RawVersoWrapper)
