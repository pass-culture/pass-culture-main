import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'

class InventoryPage extends Component {
  render = () => {
    return <main className="page">PINS</main>
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect((state, ownProps) => ({ a: 1 }), { requestData })
)(InventoryPage)
