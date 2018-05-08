import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OffererEditButton from '../OffererEditButton'
import OffersGroupsList from '../OffersGroupsList'
import OfferNewButton from '../OfferNewButton'
import withLogin from '../hocs/withLogin'
import SearchInput from '../layout/SearchInput'
import PageWrapper from '../layout/PageWrapper'
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
      <PageWrapper name="offerer is-6">
        <div className="">
          <OfferNewButton />
          <OffererEditButton />
          <SearchInput collectionName="offers" isLoading />
        </div>
        <OffersGroupsList />
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(state => ({ user: state.user }), { requestData, setUserOfferer })
)(OffererPage)
