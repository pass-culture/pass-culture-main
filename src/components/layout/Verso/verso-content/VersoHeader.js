import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Draggable from 'react-draggable'

import getRemovedDetailsUrl from '../../../../helpers/getRemovedDetailsUrl'
import { getPageY } from '../../../../utils/getPageY'

const toRectoDraggableBounds = {
  bottom: 0,
  left: 0,
  right: 0,
  top: 0,
}

class VersoHeader extends Component {
  handleStopDrag = event => {
    const { height, history, location, match, verticalSlideRatio } = this.props
    const shiftedDistance = -(height / 2) + getPageY(event)
    const thresholdDistance = height * verticalSlideRatio
    if (shiftedDistance > thresholdDistance) {
      const nextUrl = getRemovedDetailsUrl(location, match)
      if (nextUrl) {
        history.push(nextUrl)
      }
    }
  }

  render() {
    const { backgroundColor, subtitle, title } = this.props
    return (
      <div
        className="verso-header with-triangle is-relative pc-theme-black py32 px12"
        style={{ backgroundColor }}
      >
        {title && (
          <h1
            className="fs40 is-medium is-hyphens"
            id="verso-offer-name"
            style={{ lineHeight: '2.7rem' }}
          >
            {title}
            <Draggable
              axis="y"
              bounds={toRectoDraggableBounds}
              onStop={this.handleStopDrag}
            >
              <div className="drag" />
            </Draggable>
          </h1>
        )}
        {subtitle && (
          <h2
            className="fs22 is-normal is-hyphens"
            id="verso-offer-venue"
          >
            {subtitle}
          </h2>
        )}
      </div>
    )
  }
}

VersoHeader.defaultProps = {
  height: 0,
  subtitle: null,
  title: null,
  verticalSlideRatio: 0.2,
}

VersoHeader.propTypes = {
  backgroundColor: PropTypes.string.isRequired,
  height: PropTypes.number,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  subtitle: PropTypes.string,
  title: PropTypes.string,
  verticalSlideRatio: PropTypes.number,
}

export default VersoHeader
