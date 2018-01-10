import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OfferItem from '../components/OfferItem'
import OfferNew from '../components/OfferNew'
import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/request'

/*
{ alignItems: 'center',
  display: 'flex',
  height: '100vh',
  justifyContent: 'space-between'
}
*/

class SpreadsheetPage extends Component {
  handleRequestData = props => {
    const { requestData, sellerId } = this.props
    sellerId && requestData('GET', 'offers?sellerId=${sellerId}')
  }
  componentWillMount () {
    this.props.sellerId && this.handleRequestData(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.sellerId && nextProps.sellerId !== this.props.sellerId) {
      this.handleRequestData(nextProps)
    }
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

export default compose(
  withLogin,
  connect(
    ({ request: { offers }, user }) =>
      ({ offers, sellerId: user && user.sellerId }),
    { requestData }
  )
)(SpreadsheetPage)
