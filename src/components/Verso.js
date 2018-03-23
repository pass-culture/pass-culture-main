import classnames from 'classnames'
import React, { Component } from 'react'
import { rgb_to_hsv } from 'colorsys'

import ControlBar from './ControlBar'
import OfferInfo from '../components/OfferInfo'
import Booking from '../components/Booking'

class Verso extends Component {

  constructor () {
    super ()
    this.state = {
      step: 'infos',
      headerStyle: {},
    };
  }

  componentDidMount() {
    this.setHeaderStyle(this.props.backgroundColor);
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.backgroundColor !== nextProps.backgroundColor) {
      this.setHeaderStyle(nextProps.backgroundColor);
    }
  }

  setHeaderStyle(color) {
    if (color) {
      const [red, green, blue] = color;
      const {h} = rgb_to_hsv(red, green, blue);
      this.setState({
        headerStyle: {backgroundColor: `hsl(${h}, 100%, 15%)`}
      });
    }
  }

  render() {
    const {
      // deckElement,
      isFlipped,
      chosenOffer,
      id,
    } = this.props
    return (
      <div className={classnames('verso absolute', {
        'verso--flipped': isFlipped,
        'verso--booking': this.state.step === 'booking'
      })}>
        <div className='bg-wrapper'>
          <div className='verso-header' style={this.state.headerStyle}>
            <h2> { chosenOffer.thing.name }, de { chosenOffer.thing.extraData.author } </h2>
            <h6> {chosenOffer.venue.name} </h6>
          </div>
          {this.state.step === 'infos' && <ControlBar onClickBook={e => this.setState({step: 'booking'})} {...this.props} />}
          <div className='content'>
            {this.state.step === 'infos' && <OfferInfo {...chosenOffer} />}
            {this.state.step === 'booking' && (
              <Booking
                onClickCancel={e => this.setState({step: 'infos'})}
                onClickFinish={e => this.props.handleFlipCard()}
                chosenOffer={chosenOffer}
                id={id}
              />
            )}
          </div>
        </div>
      </div>
    )
  }
}

export default Verso
