import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'

import OfferersGrid from '../OfferersGrid'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import SearchInput from '../layout/SearchInput'
import { stopBodyScrolling } from '../../utils/scroll'

class ManagementPage extends Component {
  componentWillMount () {
    stopBodyScrolling(true)
  }

  render () {
    return (
      <PageWrapper name="management">
        <nav className="level is-mobile">
          <div className="level-left">
            <NavLink to='/gestion/creation/espace'>
              <button className="button is-primary level-item">
                Nouvel espace
              </button>
            </NavLink>
          </div>
        </nav>
        <nav className="level is-mobile">
          <SearchInput collectionName="offerers" isLoading />
        </nav>
        <OfferersGrid />
      </PageWrapper>
    )
  }
}

export default withLogin({ isRequired: true })(ManagementPage)
