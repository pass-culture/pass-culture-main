import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'
import OfferersList from '../OfferersList'
import SearchInput from '../layout/SearchInput'
import collectionToPath from '../../utils/collectionToPath'

class OfferersPage extends Component {
  render() {
    const {
      offerers
    } = this.props
    return (
      <PageWrapper name="profile" loading={!offerers}>
        <h1 className="title has-text-centered">Vos lieux</h1>
        <nav className="level is-mobile">
          <NavLink to={`/${collectionToPath('venues')}/nouveau`}>
            <button className="button is-primary level-item">
              Nouveau lieu
            </button>
          </NavLink>
        </nav>
        <nav className="level is-mobile">
          <SearchInput collectionNames={["events", "things"]} isLoading />
        </nav>
        <OfferersList />
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    state => ({
      user: state.user,
      offerers: get(state, 'user.offerers')
    })
  )
)(OfferersPage)
