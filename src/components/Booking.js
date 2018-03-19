import React, { Component } from 'react'

class Booking extends Component {
  onClickConfirm = event => {
    console.log('OUAI')
  }
  render () {
    return (
      <div>
        C est ici que oui on dit j'achete allez ma gueule.
        <button className='button button--alive'
          onClick={this.onClickConfirm}>
          Confirmer
        </button>
      </div>
    )
  }
}

export default Booking
