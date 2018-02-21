import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

class OffererSetting extends Component {
  render () {
    const { offerProviders } = this.props
    return (
      <div className='offer-setting'>
        <div className='h2 mb2'>
          Mes sources
        </div>
        <div>
        {
          offerProviders.map((offerProvider, index) => (
            <div className='flex items-center justify-center mb1' key={index}>
              <input className='input--checkbox mr1'
                type='checkbox' />
              <div>
                {offerProvider}
              </div>
            </div>
          ))
        }
        </div>
      </div>
    )
  }
}

export default compose(
  connect(
    state => state.user && state.user.offerer
  )
)(OffererSetting)
