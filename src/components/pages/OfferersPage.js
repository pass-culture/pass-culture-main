import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import OfferersList from '../OfferersList'
import SearchInput from '../layout/SearchInput'

const OfferersPage = ({ user, offerers }) => {
  return (
    <PageWrapper name="profile" loading={!offerers} notification={offerers && offerers.length === 1 && !offerers[0].isActive && {
      type: 'success',
      text: 'Le rattachement de la structure a été demandé. Vous allez recevoir la dernière étape d\'inscription par e-mail.'
    }}>
      <h1 className="title is-size-1 has-text-grey is-italic">Vos structures</h1>
      <p className="subtitle">Retrouvez ici la ou les structures dont vous gérez les offres Pass Culture.</p>
      {false && (
        <nav className="level is-mobile">
          <SearchInput
            collectionNames={["offerers"]}
            config={{
              isMergingArray: false,
              key: 'searchedOfferers'
            }}
            isLoading
          />
        </nav>
      )}
      <OfferersList />
      <nav className="level is-mobile">
        <NavLink to={`/structures/nouveau`}>
          <button className="button is-primary is-small is-outlined level-item">
            Rattacher une structure
          </button>
        </NavLink>
      </nav>
    </PageWrapper>
  )
}


export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      offerers: state.data.offerers
    }))
)(OfferersPage)
