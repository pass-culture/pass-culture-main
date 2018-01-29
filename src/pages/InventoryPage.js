import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'

class InventoryPage extends Component {
  render = () => {
    return (
      <main className='page'>
        PINS
      </main>
    )
  }
}

export default connect(
  (state, ownProps) => ({ a: 1 }),
  { requestData }
)(InventoryPage)
