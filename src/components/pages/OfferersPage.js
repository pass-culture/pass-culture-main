import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import Icon from '../layout/Icon'
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
      <div className="level is-vcentered">
        <h1 className="is-size-1 has-text-grey is-italic level-left">
          Vos structures
        </h1>
        <div className="level-right">
          <NavLink to={`/structures/nouveau`}>
            <span className='icon'>
              <Icon svg={'ico-guichet-w'} />
            </span>
            <button className="button is-primary">
              Rattacher une structure
            </button>
          </NavLink>
        </div>
      </div>

      <br />
      <p className="subtitle">
        Retrouvez ici la ou les structures dont vous gérez les offres Pass Culture.
      </p>

      <br />
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
