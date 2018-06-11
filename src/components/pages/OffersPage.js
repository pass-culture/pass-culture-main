import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import OccasionsList from '../OccasionsList'
import withLogin from '../hocs/withLogin'
import Icon from '../layout/Icon'
import SearchInput from '../layout/SearchInput'
import PageWrapper from '../layout/PageWrapper'
import selectOccasions from '../../selectors/occasions'


class OffersPage extends Component {
  handleRequestData = () => {
    this.props.requestData('GET', 'occasions')
  }

  componentDidMount() {
    this.props.user && this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { user } = this.props
    if (user && user !== prevProps.user) {
      this.handleRequestData()
    }
  }

  render() {
    const { occasions } = this.props
    return (
      <PageWrapper name="offers" loading={!occasions.length}>
        <div className="level is-vcentered">
          <h1 className='is-size-1 has-text-grey is-italic level-left'>
            Vos offres
          </h1>
          <div className="level-right">
            <NavLink to={`/offres/evenements/nouveau`}>
              <button className="button is-primary level-item">
                Ajouter une offre
              </button>
            </NavLink>
          </div>
        </div>

        <br />
        <p className="subtitle">
          Voici toutes vos offres apparaissant dans le Pass Culture.
        </p>

        <br />
        <p className="search level-left">
          Rechercher une offre:
        </p>
        <nav className="level is-mobile">
          <SearchInput
            collectionNames={["events", "things"]}
            config={{
              isMergingArray: false,
              key: 'searchedOccasions'
            }}
            isLoading
          />
          <button>
            <Icon svg={'ico-guichet-w'} />
          </button>
        </nav>
        {occasions.length && <OccasionsList />}
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      occasions: selectOccasions(state, ownProps),
      user: state.user
    })
  )
)(OffersPage)
