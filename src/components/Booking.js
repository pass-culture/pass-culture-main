import React, { Component } from 'react'

class Booking extends Component {
  onClickConfirm = event => {
    console.log('OUAI')
  }
  render () {
    return (
      <div>
        <div className='mb2'>
          C est ici que oui on dit j'achete allez ma gueule.
        </div>
        <button className='button button--alive'
          onClick={this.onClickConfirm}>
          Confirmer
        </button>
      </div>
    )
  }
}

export default Booking
