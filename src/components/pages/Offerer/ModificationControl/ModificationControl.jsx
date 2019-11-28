import { CancelButton, recursiveMap, SubmitButton } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'

const ModificationControl = ({ adminUserOfferer, parseFormChild, offerer, query }) => {
  const { readOnly } = query.context()
  const { id } = offerer || {}

  const fragment = (
    <Fragment>
      <div className="control">
        {readOnly ? (
          adminUserOfferer && (
            <NavLink
              className="button is-secondary is-medium"
              to={`/structures/${id}?modification`}
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
              <SubmitButton className="button is-primary is-medium">
                {'Valider'}
              </SubmitButton>
            </div>
          </div>
        )}
      </div>
      <br />
    </Fragment>
  )

  return recursiveMap(
    fragment,
    parseFormChild
  )
}

ModificationControl.isParsedByForm = true

ModificationControl.defaultProps = {
  adminUserOfferer: false,
}

ModificationControl.propTypes = {
  adminUserOfferer: PropTypes.bool,
  offerer: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }),
  parseFormChild: PropTypes.func.isRequired,
  query: PropTypes.shape().isRequired,
}

export default ModificationControl
