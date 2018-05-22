import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import OffersGroupsList from '../OffersGroupsList'
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
    const { offererId } = this.props
    return (
      <PageWrapper name="offerer">
        <nav className="level is-mobile">
          <div className="level-left">
            <NavLink to={`/gestion/${offererId}/espace`}>
              <button className="button is-primary level-item">
                Configurer mon espace
              </button>
            </NavLink>
            <NavLink to={`/gestion/${offererId}/creation`}>
              <button className="button is-primary level-item">
                Nouvelle Offre
              </button>
            </NavLink>
          </div>
        </nav>
        <nav className="level is-mobile">
          <SearchInput collectionName="offers" isLoading />
        </nav>
        <OffersGroupsList />
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(state => ({ user: state.user }), { requestData, setUserOfferer })
)(OffererPage)
