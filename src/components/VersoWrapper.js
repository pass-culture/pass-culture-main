import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Booking from '../components/Booking'
import ControlBar from './ControlBar'
import OfferInfo from '../components/OfferInfo'
import MenuButton from '../components/layout/MenuButton'

import { ROOT_PATH } from '../utils/config';
import selectHeaderColor from '../selectors/headerColor'
import selectSource from '../selectors/source'
import selectVenue from '../selectors/venue'

class Verso extends Component {

  constructor () {
    super ()
    this.state = {
      step: 'infos',
    };
  }

  render() {
    const {
      headerColor,
      isFlipped,
      source,
      venue
    } = this.props
    const { step } = this.state
    const author = source.extraData && source.extraData.author
    return (
      <div className='verso-wrapper' style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-k.svg')` }}>
        <div className='verso-header' style={{ backgroundColor: headerColor }}>
          <h2> { source.name }, { author && ("de " + author) } </h2>
          <h6> { venue.name } </h6>
        </div>
        {this.props.hasControlBar && <ControlBar />}
        <div className='content'>
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
