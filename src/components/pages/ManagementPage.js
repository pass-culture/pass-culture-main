import React from 'react'
import { NavLink } from 'react-router-dom'

import OccasionsList from '../OccasionsList'
import withLogin from '../hocs/withLogin'
import SearchInput from '../layout/SearchInput'
import PageWrapper from '../layout/PageWrapper'

const ManagementPage = () => {
  return (
    <PageWrapper name="offerer">
      <nav className="level is-mobile">
        <NavLink to={`/gestion/creation`}>
          <button className="button is-primary level-item">
            Nouvelle Offre
          </button>
        </NavLink>
      </nav>
      <nav className="level is-mobile">
        <SearchInput collectionNames={["events", "things"]} isLoading />
      </nav>
      <OccasionsList />
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(ManagementPage)
