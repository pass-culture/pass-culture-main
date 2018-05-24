import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import { assignData, requestData } from '../../reducers/data'

import OccasionsList from '../OccasionsList'
import withLogin from '../hocs/withLogin'
import SearchInput from '../layout/SearchInput'
import PageWrapper from '../layout/PageWrapper'

class OffersPage extends Component {
  handleRequestData = () => {
    this.props.requestData('GET', `occasions`)
  }

  componentDidMount() {
    this.props.user && this.handleRequestData()
  }

  render() {
    return (
      <PageWrapper name="offerer" loading={!this.props.occasions.length}>
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
        {this.props.occasions.length && <OccasionsList />}
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(
    state => ({
      occasions: state.data.occasions || [],
      user: state.user
    }),
    { assignData, requestData }
  )
)(OffersPage)
