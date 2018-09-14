/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'

import { getDepartementByCode } from '../../helpers'

const EMPTY_FIED_PLACEHOLDER = 'Non renseigné'

const renderInformation = (label, key, value, disabled = false) => {
  // const cssclass = `${cssclass} ${(disabled && 'no-pointer') || ''}`
  const strvalue =
    (typeof value === 'string' && value.trim() !== '' && value) || false
  return (
    <div key={key} className="item dotted-bottom-black">
      <NavLink
        to={`/profil/${key}`}
        className="pc-text-button text-left no-decoration flex-columns items-center pt20 pb22"
      >
        {/* label */}
        <span className="is-block flex-1">
          <span className="pc-label pb3 is-block is-grey-text is-uppercase fs13">
            {label}
          </span>
          {/* label */}
          {strvalue && (
            <b className="is-block is-black-text fs18">{strvalue}</b>
          )}
          {/* placeholder */}
          {!strvalue && (
            <span className="is-block is-grey-text fs18">
              {EMPTY_FIED_PLACEHOLDER}
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

const MesInformations = ({ provider }) => {
  const dptCode = provider.departementCode
  const departementName = getDepartementByCode(dptCode)
  const departement = `${dptCode} - ${departementName}`
  const keys = [
    {
      disabled: false,
      key: 'publicName',
      label: 'Identifiant',
      value: provider.publicName,
    },
    {
      disabled: true,
      key: 'firstnameLastname',
      label: 'Nom et prénom',
      value: '',
    },
    {
      disabled: false,
      key: 'email',
      label: 'Adresse e-mail',
      value: provider.email,
    },
    {
      disabled: true,
      key: 'password',
      label: 'Mot de passe',
      value: false,
    },
    {
      disabled: true,
      key: 'departementCode',
      label: 'Département de résidence',
      value: departement,
    },
  ]
  // NOTE: [PERF] on calcule la longueur en dehors d'un boucle
  // https://www.w3schools.com/js/js_performance.asp
  const maxlen = keys.length - 1
  return (
    <div id="mes-informations" className="pb40 pt20">
      <h3 className="dotted-bottom-primary is-primary-text is-uppercase pb12 px12">
        <i>Mes Informations</i>
      </h3>
      <div className="px12 list">
        {keys.map((obj, index) => {
          const islast = index >= maxlen
          return renderInformation(
            obj.label,
            obj.key,
            obj.value,
            obj.disabled,
            islast
          )
        })}
      </div>
    </div>
  )
}

MesInformations.propTypes = {
  provider: PropTypes.object.isRequired,
}

export default MesInformations
