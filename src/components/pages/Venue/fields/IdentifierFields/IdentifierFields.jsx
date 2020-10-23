import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'
import { removeWhitespaces } from 'react-final-form-utils'
import ReactTooltip from 'react-tooltip'

import Icon from 'components/layout/Icon'
import HiddenField from 'components/layout/form/fields/HiddenField'
import TextareaField from 'components/layout/form/fields/TextareaField'
import TextField from 'components/layout/form/fields/TextField'

import { formatSiret } from '../../siret/formatSiret'
import VenueLabel from '../../ValueObjects/VenueLabel'
import VenueType from '../../ValueObjects/VenueType'

import getLabelFromList from './utils/getLabelFromList'
import siretValidate from './validators/siretValidate'

const parseSiret = value => {
  return value.replace(/[^[0-9]/g, '')
}

class IdentifierFields extends PureComponent {
  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  handleRenderValue = (fieldReadOnlyBecauseFrozenFormSiret, readOnly) => () => {
    if (readOnly) {
      return null
    }
    if (fieldReadOnlyBecauseFrozenFormSiret) {
      return (
        <span
          className="button"
          data-place="bottom"
          data-tip="<p>Il n’est pas possible de modifier le nom, l’addresse et la géolocalisation du lieu quand un siret est renseigné.</p>"
          data-type="info"
        >
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
        data-type="info"
      >
        <Icon svg="picto-info" />
      </span>
    )
  }

  handleRender = readOnly => () => {
    if (readOnly) {
      return null
    }
    return (
      <span
        className="button"
        data-place="bottom"
        data-tip="<p>Cette adresse recevra les e-mails de notification de réservation (sauf si une adresse différente est saisie lors de la création d’une offre)</p>"
        data-type="info"
      >
        <Icon svg="picto-info" />
      </span>
    )
  }

  commentValidate = comment => {
    const { formSiret } = this.props

    const formatedSiret = removeWhitespaces(formSiret)

    if (formatedSiret && formatedSiret.length === 14) {
      return ''
    }
    if (comment === undefined || comment === '') {
      return 'Ce champ est obligatoire'
    }
    return ''
  }

  venueTypeValidate = venueType => {
    if (venueType === undefined || venueType === '') {
      return 'Ce champ est obligatoire'
    }
    return ''
  }

  render() {
    const {
      fieldReadOnlyBecauseFrozenFormSiret,
      initialSiret,
      isCreatedEntity,
      readOnly,
      venueLabels,
      venueLabelId,
      venueTypes,
      venueTypeId,
    } = this.props

    const siretLabel = isCreatedEntity
      ? 'SIRET du lieu qui accueille vos offres (si applicable) : '
      : 'SIRET : '

    const venueTypeLabel = getLabelFromList(venueTypes, venueTypeId)
    const venueLabelText = getLabelFromList(venueLabels, venueLabelId)

    return (
      <div className="section identifier-field-section">
        <h2 className="main-list-title">
          {'Informations lieu'}
          {!readOnly && (
            <span className="required-fields-hint">
              {'Les champs marqués d’un'}
              <span className="required-legend">
                {' * '}
              </span>
              {' sont obligatoires'}
            </span>
          )}
        </h2>
        <div className="field-group">
          {isCreatedEntity && <HiddenField name="managingOffererId" />}
          <TextField
            format={formatSiret}
            label={siretLabel}
            name="siret"
            parse={parseSiret}
            readOnly={readOnly || initialSiret !== null}
            renderValue={this.handleRenderValue(fieldReadOnlyBecauseFrozenFormSiret, readOnly)}
            type="siret"
            validate={initialSiret ? undefined : siretValidate}
          />
          <TextField
            label="Nom du lieu : "
            name="name"
            readOnly={readOnly || fieldReadOnlyBecauseFrozenFormSiret}
            required
          />
          <TextField
            label="Nom d’usage du lieu : "
            name="publicName"
            readOnly={readOnly}
          />
          <TextField
            label="E-mail : "
            name="bookingEmail"
            readOnly={readOnly}
            renderValue={this.handleRender(readOnly)}
            required
            type="email"
          />
          <TextareaField
            label="Commentaire (si pas de SIRET) : "
            name="comment"
            readOnly={readOnly}
            rows={1}
            validate={this.commentValidate}
          />
          <div
            className={classnames('field field-select is-label-aligned', {
              readonly: readOnly,
            })}
          >
            <div className="field-label">
              <label htmlFor="venue-type">
                {'Type de lieu : '}
              </label>
              <span className="field-asterisk">
                {'*'}
              </span>
            </div>

            <div className="field-control">
              {!readOnly ? (
                <div className="control control-select">
                  <div
                    className={classnames('select', {
                      readonly: readOnly,
                    })}
                  >
                    <Field
                      component="select"
                      disabled={readOnly}
                      id="venue-type"
                      name="venueTypeId"
                      required
                      validate={this.venueTypeValidate}
                    >
                      <option value="">
                        {'Choisissez un type de lieu dans la liste'}
                      </option>
                      {venueTypes.map(venueType => (
                        <option
                          key={`venue-type-${venueType.id}`}
                          value={venueType.id}
                        >
                          {venueType.label}
                        </option>
                      ))}
                    </Field>
                  </div>
                </div>
              ) : (
                <div
                  className="venue-type-label"
                  id="venue-type"
                >
                  <span>
                    {venueTypeLabel}
                  </span>
                </div>
              )}
            </div>
          </div>
          <div
            className={classnames('field field-select is-label-aligned', {
              readonly: readOnly,
            })}
          >
            <div className="field-label">
              <label htmlFor="venue-label">
                {'Label du lieu :'}
              </label>
            </div>

            <div className="field-control">
              {!readOnly ? (
                <div className="control control-select">
                  <div
                    className={classnames('select', {
                      readonly: readOnly,
                    })}
                  >
                    <Field
                      component="select"
                      disabled={readOnly}
                      id="venue-label"
                      name="venueLabelId"
                    >
                      <option value="">
                        {'Choisissez un label dans la liste'}
                      </option>
                      {venueLabels.map(venueLabel => (
                        <option
                          key={`venue-label-${venueLabel.id}`}
                          value={venueLabel.id}
                        >
                          {venueLabel.label}
                        </option>
                      ))}
                    </Field>
                  </div>
                </div>
              ) : (
                <div
                  className="venue-label-label"
                  id="venue-label"
                >
                  <span>
                    {venueLabelText}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }
}

IdentifierFields.defaultProps = {
  fieldReadOnlyBecauseFrozenFormSiret: false,
  formSiret: null,
  initialSiret: null,
  isCreatedEntity: false,
  readOnly: true,
  venueLabelId: null,
  venueTypeId: null,
}

IdentifierFields.propTypes = {
  fieldReadOnlyBecauseFrozenFormSiret: PropTypes.bool,
  formSiret: PropTypes.string,
  initialSiret: PropTypes.string,
  isCreatedEntity: PropTypes.bool,
  readOnly: PropTypes.bool,
  venueLabelId: PropTypes.string,
  venueLabels: PropTypes.arrayOf(PropTypes.instanceOf(VenueLabel)).isRequired,
  venueTypeId: PropTypes.string,
  venueTypes: PropTypes.arrayOf(PropTypes.instanceOf(VenueType)).isRequired,
}

export default IdentifierFields
