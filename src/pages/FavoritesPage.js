import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'

class FavoritesPage extends Component {
  render = () => {
    return (
      <main className='page'>
        TODO
      </main>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({ a: 1 }),
    { requestData }
  )
)(FavoritesPage)
