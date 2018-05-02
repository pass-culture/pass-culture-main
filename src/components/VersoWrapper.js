import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import ControlBar from './ControlBar'
import selectCurrentHeaderColor from '../selectors/currentHeaderColor'
import selectCurrentSource from '../selectors/currentSource'
import selectCurrentVenue from '../selectors/currentVenue'
import selectIsCurrentTuto from '../selectors/isCurrentTuto'
import { ROOT_PATH } from '../utils/config'

class VersoWrapper extends Component {
  componentDidUpdate(prevProps, prevState) {
    if (!this.props.isFlipped && prevProps.isFlipped) {
      this.element.scrollTo(0, 0)
    }
  }

  render() {
    const {
      children,
      className,
      headerColor,
      source,
      venue,
      hasControlBar,
      isCurrentTuto,
    } = this.props
    const contentStyle = {}
    if (isCurrentTuto) {
      contentStyle.backgroundColor = headerColor
    } else {
      contentStyle.backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
    }
    const author = get(source, 'extraData.author')
    return (
      <div className={`verso-wrapper ${className || ''}`}>
        <div
          className="verso-header"
          style={{ backgroundColor: headerColor }}
          ref={element => (this.element = element)}
        >
          <h2>
            {' '}
            {source && source.name}
            {author && ', de ' + author}{' '}
          </h2>
          <h6> {venue && venue.name} </h6>
        </div>
        {hasControlBar && <ControlBar />}
        <div className="verso-content" style={{ ...contentStyle }}>
          {children}
        </div>
      </div>
    )
  }
}

export default connect(state => ({
  headerColor: selectCurrentHeaderColor(state),
  isFlipped: state.verso.isFlipped,
  isCurrentTuto: selectIsCurrentTuto(state),
  source: selectCurrentSource(state),
  venue: selectCurrentVenue(state),
}))(VersoWrapper)
