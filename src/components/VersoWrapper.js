import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import ControlBar from './ControlBar'

import { ROOT_PATH } from '../utils/config';
import selectHeaderColor from '../selectors/headerColor'
import selectSource from '../selectors/source'
import selectVenue from '../selectors/venue'

class Verso extends Component {

  render() {
    const {
      className,
      headerColor,
      source,
      venue,
    } = this.props
    const author = get(source, 'extraData.author')
    return (
      <div className={`verso-wrapper ${className || ''}`}>
        <div className='verso-header' style={{ backgroundColor: headerColor }}>
          <h2> { source && source.name }, { author && ("de " + author) } </h2>
          <h6> { venue && venue.name } </h6>
        </div>
        {this.props.hasControlBar && <ControlBar />}
        <div className='content' style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-k.svg')` }}>
          {this.props.children}
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    headerColor: selectHeaderColor(state),
    isFlipped: state.navigation.isFlipped,
    source: selectSource(state),
    venue: selectVenue(state)
  }))(Verso)
