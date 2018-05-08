import React from 'react'
import { NavLink } from 'react-router-dom'

import OfferersGrid from '../OfferersGrid'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import SearchInput from '../layout/SearchInput'


const ManagementPage = () => {
  return (
    <PageWrapper header name="management">
      <nav className="level is-mobile">
        <div className="level-left">
          <NavLink to='/offerer/new'>
            <button className="button is-primary level-item">
              Nouvel espace
            </button>
          </NavLink>
        </div>
      </nav>
      <SearchInput collectionName="offerers" isLoading />
      <OfferersGrid />
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(ManagementPage)
