import get from 'lodash.get'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import OfferersList from '../OfferersList'
import SearchInput from '../layout/SearchInput'

class OfferersPage extends Component {
  render() {
    const { user } = this.props
    return (
      <PageWrapper name="profile" loading={!get(user, 'offerers')}>
        <h1 className="title has-text-centered">Vos structures</h1>
        <nav className="level is-mobile">
          <NavLink to={`/structures/nouveau`}>
            <button className="button is-primary level-item">
              Nouvelle structure
            </button>
          </NavLink>
        </nav>
        <nav className="level is-mobile">
          <SearchInput
            collectionNames={["offerers"]}
            config={{
              isMergingArray: false,
              key: 'offerers'
            }}
            isLoading
          />
        </nav>
        <OfferersList />
      </PageWrapper>
    )
  }
}

export default withLogin({ isRequired: true })(OfferersPage)
