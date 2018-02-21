import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OffererEditButton from '../components/OffererEditButton'
import OffersList from '../components/OffersList'
import OfferNewButton from '../components/OfferNewButton'
import SearchInput from '../components/SearchInput'
import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'
import { setUserOfferer } from '../reducers/user'

class OffererPage extends Component {
  handleSetUserOfferer = props => {
    const { offererId, setUserOfferer, user } = props
    user && user.userOfferers && setUserOfferer(offererId)
  }
  componentWillMount () {
    this.props.requestData('GET', 'providers')
    this.handleSetUserOfferer(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.user && nextProps.user.userOfferers != (this.props.user && this.props.user.userOfferers)) {
      this.handleSetUserOfferer(nextProps)
    }
  }
  render () {
    return (
      <main className='page offerer-page p2'>
        <div className='flex items-center flex-start mt2 mb2'>
          <OfferNewButton />
          <OffererEditButton />
          <SearchInput />
        </div>
        <OffersList />
      </main>
    )
  }
}

export default compose(
  // withLogin,
  connect(
    state => ({ user: state.user }),
    { requestData, setUserOfferer }
  )
)(OffererPage)
