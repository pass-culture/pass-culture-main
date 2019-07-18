import get from 'lodash.get'
import { CancelButton, recursiveMap, SubmitButton } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import { NavLink } from 'react-router-dom'

import VenueItem from '../VenueItem/VenueItem'

const ModificationControl = ({ adminUserOfferer, parseFormChild, offerer, query, venues }) => {
  const { readOnly } = query.context()
  const { id } = offerer || {}
  return recursiveMap(
    <Fragment>
      <div className="control">
        {readOnly ? (
          adminUserOfferer && (
            <NavLink
              className="button is-secondary is-medium"
              to={`/structures/${id}?modifie`}
            >
              {'Modifier les informations'}
            </NavLink>
          )
        ) : (
          <div
            className="field is-grouped is-grouped-centered"
            style={{ justifyContent: 'space-between' }}
          >
            <div className="control">
              <CancelButton
                className="button is-secondary is-medium"
                to={`/structures/${id}`}
              >
                {'Annuler'}
              </CancelButton>
            </div>
            <div className="control">
              <SubmitButton className="button is-primary is-medium">{'Valider'}</SubmitButton>
            </div>
          </div>
        )}
      </div>
      <br />
      <div className="section">
        <h2 className="main-list-title">{'LIEUX'}</h2>
        <ul className="main-list venues-list">
          {venues.map(v => (
            <VenueItem
              key={v.id}
              venue={v}
            />
          ))}
        </ul>
        <div className="has-text-centered">
          <NavLink
            className="button is-secondary is-outlined"
            to={`/structures/${get(offerer, 'id')}/lieux/creation`}
          >
            {'+ Ajouter un lieu'}
          </NavLink>
        </div>
      </div>
    </Fragment>,
    parseFormChild
  )
}

ModificationControl.isParsedByForm = true

export default ModificationControl
