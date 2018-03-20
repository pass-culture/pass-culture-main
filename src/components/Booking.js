import React, { Component } from 'react'
import { connect } from 'react-redux'

class Booking extends Component {
  onClickConfirm = event => {
    const { chosenOffer, requestData } = this.props
    requestData('POST', 'bookings', {
      body: {
        offerId: chosenOffer.id,
        quantity: 1
      }
    })
  }
  render () {
    const { token } = this.props
    return (
      <div>
        <div className='mb2'>
          C est ici que oui on dit j'achete allez ma gueule.
        </div>
        {
          token
          ? (
            <div>
              Votre token
              <br />
              {token}
            </div>
          )
          : (
            <button className='button button--alive'
              onClick={this.onClickConfirm}>
              Confirmer
            </button>
          )
        }
      </div>
    )
  }
}

export default connect(
  state => (state.data.bookings && state.data.bookings[0]) || {}
)(Booking)
