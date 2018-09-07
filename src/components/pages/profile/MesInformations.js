/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { getDepartementByCode } from '../../../helpers'

const noop = () => {}

const renderInformation = (label, value, disabled = false, islast = false) => {
  const placeholder = 'Non renseigné'
  let cssclass = islast ? '' : 'dotted-bottom-black'
  cssclass = `${cssclass} ${(disabled && 'no-pointer') || ''}`
  const strvalue =
    (typeof value === 'string' && value.trim() !== '' && value) || false
  return (
    <div className="item">
      <button
        type="button"
        onClick={noop}
        className={`no-border no-outline no-background text-left is-full-width flex-columns items-center pt20 pb22 ${cssclass}`}
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
            <span className="is-block is-grey-text fs18">{placeholder}</span>
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
      </button>
    </div>
  )
}

const MesInformations = ({ provider }) => {
  const { departementCode, email, publicName } = provider
  const departementName = getDepartementByCode(departementCode)
  const departement = `${departementCode} - ${departementName}`
  return (
    <div id="mes-informations" className="mb40 mt20">
      <h3 className="dotted-bottom-primary is-primary-text is-uppercase pb8 px12">
        <i>Mes Informations</i>
      </h3>
      <div className="px12 list">
        {renderInformation('Identifiant', publicName, true)}
        {renderInformation('Nom et prénom', '', true)}
        {renderInformation('Adresse e-mail', email, true)}
        {renderInformation('Mot de passe', '', true)}
        {renderInformation('Département de résidence', departement, true, true)}
      </div>
    </div>
  )
}

MesInformations.propTypes = {
  provider: PropTypes.object.isRequired,
}

export default MesInformations
