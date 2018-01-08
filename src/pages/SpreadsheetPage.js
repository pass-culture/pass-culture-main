import React, { Component } from 'react'
import { connect } from 'react-redux'

import SpreadsheetItem from '../components/SpreadsheetItem'
import { requestData } from '../reducers/request'

/*
{ alignItems: 'center',
  display: 'flex',
  height: '100vh',
  justifyContent: 'space-between'
}
*/

class SpreadsheetPage extends Component {
  componentWillMount() {
    this.props.requestData('GET', 'pro/offers')
  }
  render () {
    const { offers } = this.props
    return (
      <main className='flex items-center justify-center' style={{ height: '100vh' }}>
        <div>
        {
          offers && offers.map((offer, index) => (
            <SpreadsheetItem key={index} {...offer} />
          ))
        }
        </div>
      </main>
    )
  }
}

export default connect(({ request: { offers } }) => ({ offers }),
  { requestData }
)(SpreadsheetPage)
