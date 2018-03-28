import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Booking from '../components/Booking'
import ControlBar from './ControlBar'
import OfferInfo from '../components/OfferInfo'
import Booking from '../components/Booking'
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
    const { headerColor,
      isFlipped,
      source,
      venue
    } = this.props
    const { step } = this.state
    const author = source.extraData && source.extraData.author
    return (
      <div className={classnames('verso absolute', {
        'verso--flipped': isFlipped,
        'verso--booking': step === 'booking'
      })} >
        <div className='bg-wrapper' style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-k.svg')` }}>
          <div className='verso-header' style={{ backgroundColor: headerColor }}>
            <h2> { source.name }, { author && ("de " + author) } </h2>
            <h6> { venue.name } </h6>
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
        {this.state.step === 'infos' && <MenuButton borderTop colored />}
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
