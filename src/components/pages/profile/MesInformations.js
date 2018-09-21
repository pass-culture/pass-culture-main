/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'

import { routes } from './page-config'

const EMPTY_FIELD_PLACEHOLDER = 'Non renseigné'

const renderInformation = (field, user) => {
  const { key, label, disabled, placeholder, resolver } = field
  // NOTE: par défaut on sette la valeur sur la clé de l'objet user
  // pour le password on ne souhaite pas affiché la valeur
  // pour ca on utilise le resolver retournant une valeur falsey
  let value = user[key]
  const route = routes[key]
  if (resolver) value = resolver(user, key)
  return (
    <div key={key} className="item dotted-bottom-black">
      <NavLink
        disabled={disabled}
        to={`/profil/${route}`}
        className="pc-text-button text-left no-decoration flex-columns items-center pt20 pb22"
      >
        {/* label */}
        <span className="is-block flex-1">
          <span className="pc-label pb3 is-block is-grey-text is-uppercase fs13">
            {label}
          </span>
          {/* label */}
          {value && <b className="is-block is-black-text fs18">{value}</b>}
          {/* placeholder */}
          {!value && (
            <span className="is-block is-grey-text fs18">
              {placeholder || EMPTY_FIELD_PLACEHOLDER}
            </span>
          )}
        </span>
        {!disabled && (
          <span className="is-block flex-0">
            <span
              aria-hidden
              className="icon-next"
              title={`Modifier ${label}`}
            />
          </span>
        )}
      </NavLink>
    </div>
  )
}

const MesInformations = ({ user, fields }) => (
  // const dptCode = user.departementCode
  // const departementName = getDepartementByCode(dptCode)
  // const departement = `${dptCode} - ${departementName}`
  <div id="mes-informations" className="pb40 pt20">
    <h3 className="dotted-bottom-primary is-primary-text is-uppercase pb12 px12">
      <i>Mes Informations</i>
    </h3>
    <div className="px12 list">
      {fields.map(obj => renderInformation(obj, user))}
    </div>
  </div>
)

MesInformations.propTypes = {
  fields: PropTypes.array.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

export default MesInformations
