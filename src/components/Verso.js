import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import ControlBar from './ControlBar'
import OfferInfo from '../components/OfferInfo'
import Booking from '../components/Booking'
import MenuButton from '../components/layout/MenuButton'

import currentUserMediation from '../selectors/currentUserMediation'
import currentOffer from '../selectors/currentOffer'
import currentHeaderColor from '../selectors/currentHeaderColor'

class Verso extends Component {

  constructor () {
    super ()
    this.state = {
      step: 'infos',
    };
  }

  render() {
    const {
      thing,
      venue,
    } = this.props.currentOffer
    return (
      <div className={classnames('verso absolute', {
        'verso--flipped': this.props.isFlipped,
        'verso--booking': this.state.step === 'booking'
      })}>
        <div className='bg-wrapper'>
          <div className='verso-header' style={{backgroundColor: this.props.currentHeaderColor}}>
            <h2> { thing.name }, de { thing.extraData.author } </h2>
            <h6> {venue.name} </h6>
          </div>
          {this.state.step === 'infos' && <ControlBar onClickBook={e => this.setState({step: 'booking'})} />}
          <div className='content'>
            {this.state.step === 'infos' && <OfferInfo />}
            {this.state.step === 'booking' && (
              <Booking
                onClickCancel={e => this.setState({step: 'infos'})}
                onClickFinish={e => this.setState({step: 'infos'})}
              />
            )}
          </div>
        </div>
        {this.state.step === 'infos' && <MenuButton borderTop colored />}
      </div>
    )
  }
}

export default connect(
  state => ({
    currentOffer: currentOffer(state),
    currentUserMediation: currentUserMediation(state),
    currentHeaderColor: currentHeaderColor(state),
    isFlipped: state.navigation.isFlipped
  }))(Verso)
