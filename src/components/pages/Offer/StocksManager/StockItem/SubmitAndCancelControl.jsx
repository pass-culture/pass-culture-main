import { recursiveMap, SubmitButton } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import { NavLink } from 'react-router-dom'

const SubmitAndCancelControl = ({ offer, parseFormChild }) => {
  const { id: offerId } = offer
  const children = (
    <Fragment>
      <td>
        <SubmitButton className="button is-primary is-small submitStep">
          Valider
        </SubmitButton>
      </td>
      <td className="is-clipped">
        <NavLink
          className="button is-secondary is-small cancel-step"
          to={`/offres/${offerId}?gestion`}>
          Annuler
        </NavLink>
      </td>
    </Fragment>
  )
  return recursiveMap(children, parseFormChild)
}

export default SubmitAndCancelControl
SubmitAndCancelControl.isParsedByForm = true
