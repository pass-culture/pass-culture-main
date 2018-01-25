import React, { Component } from 'react'
import { connect } from 'react-redux'
import Swipeable from 'react-swipeable'

import { requestData } from '../reducers/data'

class OffersSwipe extends Component {
  componentWillMount = () => {
    const { requestData } = this.props;
    requestData('GET', `offers?hasPrice=true`)
  }
  onSwipingDown = () => {
    console.log('Down')
  }
  onSwipingLeft = () => {
    console.log('Left')
  }
  onSwipingRight = () => {
    console.log('Right')
  }
  onSwipingUp = () => {
    console.log('Up')
  }
  render = () => {
    const { offers } = this.props
    return (
      <div>
        {
          offers && offers.slice(0, 1).map((offer, index) => (
            <Swipeable key={index}
              onSwipingDown={this.onSwipingDown}
              onSwipingLeft={this.onSwipingLeft}
              onSwipingRight={this.onSwipingRight}
              onSwipingUp={this.onSwipingUp}
            >
              TEST
            </Swipeable>
          ))
        }
      </div>
    )
  }
}

export default connect(
   state => ({ offers: state.data.offers }),
   { requestData }
 )(OffersSwipe)
