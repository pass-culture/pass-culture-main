/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { getDepartementByCode } from '../../../helpers'

const noop = () => {}

const renderInformation = (label, value, disabled = false, islast = false) => {
  const placeholder = 'Non renseigné'
  const cssclass = islast ? '' : 'dotted-bottom-black'
  const strvalue =
    (typeof value === 'string' && value.trim() !== '' && value) || false
  return (
    <div>
      <button
        type="button"
        onClick={noop}
        disabled={disabled}
        className={`no-border no-outline no-background text-left is-full-width flex-columns items-center pt22 pb22 ${cssclass}`}
      >
        <span className="is-block flex-1">
          <span className="pc-label pb3 is-block is-uppercase">{label}</span>
          {strvalue && <b className="is-block">{strvalue}</b>}
          {!strvalue && (
            <span className="is-block is-uppercase">{placeholder}</span>
          )}
        </span>
        <span className="is-block flex-0">
          <span aria-hidden className="icon-next" title={`Modifier ${label}`} />
        </span>
      </button>
    </div>
  )
}

const MesInformations = ({ provider }) => {
  const { departementCode, email, publicName } = provider
  const departementName = getDepartementByCode(departementCode)
  const departement = `${departementCode} - ${departementName}`
  return (
    <div className="mb40 mt20">
      <h3 className="dotted-bottom-primary is-primary-text is-uppercase pb8 px12">
        <i>Mes Informations</i>
      </h3>
      <div className="px12">
        {renderInformation('Identifiant', publicName)}
        {renderInformation('Nom et prénom', '')}
        {renderInformation('Adresse e-mail', email)}
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
