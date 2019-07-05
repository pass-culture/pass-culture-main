import PropTypes from 'prop-types'
import React from 'react'

import { siretValidate } from './validators'
import { Icon } from 'components/layout/Icon'
import {
  HiddenField,
  TextareaField,
  TextField,
} from 'components/layout/form/fields'
import { formatSirenOrSiret } from 'utils/siren'

const getIsCommentRequired = formSiret => !formSiret || formSiret.length !== 14

const buildSiretLabel = isCreatedEntity =>
  `SIRET${isCreatedEntity ? 'du lieu qui accueille vos offres (si applicable)' : ''} : `

const IdentifierFields = ({
  fieldReadOnlyBecauseFrozenFormSiret,
  formSiret,
  initialSiret,
  isCreatedEntity,
  isModifiedEntity,
  readOnly,
}) => (
  <div className="section">
    <h2 className="main-list-title is-relative">
      IDENTIFIANTS
      {!readOnly && (
        <span className="is-pulled-right is-size-7 has-text-grey">
          Les champs marqués d'un <span className="required-legend"> * </span>{' '}
          sont obligatoires
        </span>
      )}
    </h2>
    <div className="field-group">
      {isCreatedEntity && <HiddenField name="managingOffererId" />}
      <TextField
        format={formatSirenOrSiret}
        innerClassName="col-50"
        label={buildSiretLabel(isCreatedEntity)}
        name="siret"
        readOnly={readOnly || initialSiret !== null}
        renderValue={() => {
          if (readOnly) {
            return null
          }
          if (fieldReadOnlyBecauseFrozenFormSiret) {
            return (
              <span
                className="button"
                data-place="bottom"
                data-tip="<p>Il n'est pas possible de modifier le nom, l'addresse et la géolocalisation du lieu quand un siret est renseigné.</p>"
                data-type="info">
                <Icon svg="picto-info" />
              </span>
            )
          }
          return (
            <span
              className="button"
              data-place="bottom"
              data-tip="<div><p>Saisissez ici le SIRET du lieu lié à votre structure pour retrouver ses informations automatiquement.</p>
<p>Si les informations ne correspondent pas au SIRET saisi, <a href='mailto:pass@culture.gouv.fr?subject=Question%20SIRET'> contactez notre équipe</a>.</p></div>"
              data-type="info">
              <Icon svg="picto-info" />
            </span>
          )
        }}
        type="siret"
        {...(initialSiret ? {} : { validate: siretValidate })}
      />
      <TextField
        label="Nom : "
        name="name"
        readOnly={readOnly || fieldReadOnlyBecauseFrozenFormSiret}
        required
      />
      <TextField label="Nom d'usage : " name="publicName" readOnly={readOnly} />
      <TextField
        innerClassName="col-75"
        label="E-mail : "
        name="bookingEmail"
        readOnly={readOnly}
        required
        renderValue={() => {
          if (readOnly) {
            return null
          }
          return (
            <span
              className="button"
              data-tip="<p>Cette adresse recevra les e-mails de notification de réservation (sauf si une adresse différente est saisie lors de la création d'une offre)</p>"
              data-place="bottom"
              data-type="info">
              <Icon svg="picto-info" />
            </span>
          )
        }}
        type="email"
      />
      <TextareaField
        label="Commentaire (si pas de SIRET) : "
        name="comment"
        readOnly={readOnly}
        required={getIsCommentRequired(formSiret)}
        rows={1}
      />
    </div>
  </div>
)

IdentifierFields.defaultProps = {
  fieldReadOnlyBecauseFrozenFormSiret: false,
  formSiret: null,
  initialSiret: null,
  readOnly: true,
}

IdentifierFields.propTypes = {
  fieldReadOnlyBecauseFrozenFormSiret: PropTypes.bool,
  formSiret: PropTypes.string,
  initialSiret: PropTypes.string,
  isCreatedEntity: PropTypes.bool.isRequired,
  isModifiedEntity: PropTypes.bool.isRequired,
  readOnly: PropTypes.bool,
}

export default IdentifierFields
