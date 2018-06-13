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
    const {
      location: { search },
      occasions
    } = this.props
    return (
      <PageWrapper
        loading={!occasions.length}
        name="offers"
        notification={
          search === '?success=true' && {
            text: 'Ca a fonctionné cest genial de la balle de francois miterrand',
            type: 'success'
          }
        }
      >
        <NavLink to={`/offres/evenements/nouveau`} className='button is-primary is-pulled-right'>
          + Ajouter une offre
        </NavLink>
        <div className="level">
          <h1 className='pc-title'>
            Vos offres
          </h1>
          <div className="level-right">
          </div>
        </div>

        <br />
        <p className="subtitle">
          Voici toutes vos offres apparaissant dans le Pass Culture.
        </p>
        {false && <div>
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
                </div>}
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
