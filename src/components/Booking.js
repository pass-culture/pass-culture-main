import React, { Component } from 'react'
import { connect } from 'react-redux'

class Booking extends Component {
  constructor () {
    super ()
    this.state = { token: null }
  }
  onClickBookings = event => {

  }
  onClickConfirm = event => {
    const { chosenOffer, id, requestData } = this.props
    requestData('POST', 'bookings', {
      body: {
        offerId: chosenOffer.id,
        quantity: 1,
        userMediationId: id
      }
    })
  }
  handleSetToken = props => {
    const { userMediationBookings } = props
    let token = props.token
    if (!token && userMediationBookings && userMediationBookings.length === 1) {
      token = userMediationBookings[0].token
    }
    this.setState({ token })
  }
  componentWillMount () {
    this.handleSetToken(this.props)
  }
  componentWillReceiveProps (nextProps) {
    this.handleSetToken(nextProps)
  }
  render () {
    const { userMediationBookings } = this.props
    const { token } = this.state
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
        {
          userMediationBookings && userMediationBookings.length > 1 && (
            <button className='button button--alive'
              onClick={this.onClickBookings}>
              Vos autres réservations
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
