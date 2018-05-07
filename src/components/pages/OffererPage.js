import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OffererEditButton from '../OffererEditButton'
import OffersList from '../OffersList'
import OfferNewButton from '../OfferNewButton'
import SearchInput from '../layout/SearchInput'
import withLogin from '../hocs/withLogin'
import { requestData } from '../../reducers/data'
import { setUserOfferer } from '../../reducers/user'

class OffererPage extends Component {

  componentWillMount() {
    const { requestData } = this.props
    requestData('GET', 'providers')
  }

  componentWillReceiveProps(nextProps) {
    const { offererId, requestData, user } = nextProps
    if (user && this.props.user) {
      requestData('GET', `offerers/${offererId}`, { key: 'offerers' })
    }
  }

  render() {
    return (
      <main className="page offerer-page p2">
        <div className="flex items-center flex-start mt2 mb2">
          <OfferNewButton />
          <OffererEditButton />
          <SearchInput collectionName="offers" isLoading />
        </div>
        <OffersList />
      </main>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(state => ({ user: state.user }), { requestData, setUserOfferer })
)(OffererPage)
