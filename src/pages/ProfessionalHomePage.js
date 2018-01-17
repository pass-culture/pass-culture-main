import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OfferItem from '../components/OfferItem'
import OfferNewButton from '../components/OfferNewButton'
import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'

class ProfessionalHomePage extends Component {
  handleRequestData = props => {
    const { requestData, sellerId } = props
    if (!this.hasRequired && sellerId) {
      requestData('GET', `offers?sellerId=${sellerId}`)
      this.hasRequired = true
    }
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
      <main className='professional-home-page p2'>
        <div className='flex items-center flex-start mt2'>
          <OfferNewButton />
        </div>
        <div className='md-col-9 mx-auto'>
          {
            offers && offers.map((offer, index) => (
              <OfferItem isModify key={index} {...offer} />
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
    state =>({
      offers: state.data.offers,
      sellerId: state.user && state.user.sellerId
    }),
    { requestData }
  )
)(ProfessionalHomePage)
