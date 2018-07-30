import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

class InventoryPage extends Component {
  render = () => {
    return <main className="page">PINS</main>
  }
}

export default connect(
  null,
  { requestData }
)(InventoryPage)
