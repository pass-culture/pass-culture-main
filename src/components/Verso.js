import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferInfo from '../components/OfferInfo'
import VersoWrapper from '../components/VersoWrapper'
import MenuButton from '../components/layout/MenuButton'

class Verso extends Component {

  render() {
    return (
      <div className={classnames('verso', {
        'flipped': this.props.isFlipped,
      })} >
        <VersoWrapper hasControlBar className='with-padding-top'>
          <OfferInfo />
        </VersoWrapper>
        <MenuButton borderTop colored />
      </div>
    )
  }
}

export default connect(
  state => ({
    isFlipped: state.navigation.isFlipped,
  }))(Verso)
