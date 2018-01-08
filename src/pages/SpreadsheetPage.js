import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferItem from '../components/OfferItem'
import OfferNew from '../components/OfferNew'
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
    this.props.requestData('GET', 'offers', { type: 'professional' })
  }
  render () {
    const { offers } = this.props
    return (
      <main className='page flex items-center justify-center'>
        <div>
          <OfferNew />
          {
            offers && offers.map((offer, index) => (
              <OfferItem key={index} {...offer} />
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
