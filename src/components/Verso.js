import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import ControlBar from './ControlBar'
import OfferInfo from '../components/OfferInfo'
import Booking from '../components/Booking'
import selectCurrentHeaderColor from '../selectors/currentHeaderColor'
import selectCurrentSource from '../selectors/currentSource'
import selectCurrentVenue from '../selectors/currentVenue'

class Verso extends Component {

  constructor () {
    super ()
    this.state = {
      step: 'infos',
    };
  }

  render() {
    const { currentHeaderColor,
      currentSource,
      currentVenue,
      isFlipped
    } = this.props
    const { step } = this.state
    const author = currentSource.extraData && currentSource.extraData.author
    return (
      <div className={classnames('verso absolute', {
        'verso--flipped': isFlipped,
        'verso--booking': step === 'booking'
      })} >
        <div className='bg-wrapper'>
          <div className='verso-header' style={{ backgroundColor: currentHeaderColor }}>
            <h2> { currentSource.name }, { author && ("de " + author) } </h2>
            <h6> { currentVenue.name } </h6>
          </div>
          { step === 'infos' && <ControlBar onClickBook={e => this.setState({step: 'booking'})} />}
          <div className='content'>
            { step === 'infos' && <OfferInfo />}
            { step === 'booking' && (
              <Booking onClickCancel={e => this.setState({step: 'infos'})}
                onClickFinish={e => this.setState({step: 'infos'})} />
            )}
          </div>
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    currentHeaderColor: selectCurrentHeaderColor(state),
    currentSource: selectCurrentSource(state),
    currentVenue: selectCurrentVenue(state),
    isFlipped: state.navigation.isFlipped
  }))(Verso)
