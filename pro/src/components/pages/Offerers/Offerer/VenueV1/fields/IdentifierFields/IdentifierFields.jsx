import React, { PureComponent } from 'react'

import { CheckboxField } from 'ui-kit'
import { Field } from 'react-final-form'
import HiddenField from 'components/layout/form/fields/HiddenField'
import Icon from 'components/layout/Icon'
import PropTypes from 'prop-types'
import ReactTooltip from 'react-tooltip'
import { SiretField } from 'components/layout/form/fields/SiretField'
import TextField from 'components/layout/form/fields/TextField'
import TextareaField from 'components/layout/form/fields/TextareaField'
import VenueLabel from 'components/pages/Offerers/Offerer/VenueV1/ValueObjects/VenueLabel'
import VenueType from 'components/pages/Offerers/Offerer/VenueV1/ValueObjects/VenueType'
/*eslint no-undef: 0*/
import classnames from 'classnames'
import getLabelFromList from './utils/getLabelFromList'
import { removeWhitespaces } from 'react-final-form-utils'

class IdentifierFields extends PureComponent {
  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  handleTooltipBookingEmail = readOnly => () =>
    readOnly ? null : (
      <span
        className="button"
        data-place="bottom"
        data-tip="<p>Cette adresse recevra les e-mails de notification de réservation (sauf si une adresse différente est saisie lors de la création d’une offre)</p>"
        data-type="info"
      >
        <Icon svg="picto-info" />
      </span>
    )

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
      isDirtyFieldBookingEmail,
      readOnly,
      venueIsVirtual,
      venueLabels,
      venueLabelId,
      venueTypes,
      venueTypeCode,
    } = this.props

    const venueTypesWithoutVirtualOffer = venueTypes.filter(
      venueType => venueType.label !== 'Offre numérique'
    )

    const siretLabel = isCreatedEntity
      ? 'SIRET du lieu qui accueille vos offres (si applicable) : '
      : 'SIRET : '

    const venueTypeLabel = getLabelFromList(venueTypes, venueTypeCode)
    const venueLabelText = getLabelFromList(venueLabels, venueLabelId)

    return (
      <div className="section identifier-field-section">
        <h2 className="main-list-title">
          Informations lieu
          {!readOnly && (
            <span className="required-fields-hint">
              Les champs marqués d’un <span className="required-legend">*</span>{' '}
              sont obligatoires
            </span>
          )}
        </h2>
        <div className="field-group">
          {isCreatedEntity && <HiddenField name="managingOffererId" />}
          {!venueIsVirtual && (
            <SiretField
              label={siretLabel}
              readOnly={readOnly || initialSiret !== null}
            />
          )}
          <TextField
            label="Nom du lieu : "
            name="name"
            readOnly={readOnly || fieldReadOnlyBecauseFrozenFormSiret}
            required
          />
          {!venueIsVirtual && (
            <TextField
              label="Nom d’usage du lieu : "
              name="publicName"
              readOnly={readOnly}
            />
          )}
          <TextField
            label="Mail : "
            name="bookingEmail"
            readOnly={readOnly}
            renderTooltip={this.handleTooltipBookingEmail(readOnly)}
            required={!venueIsVirtual}
            type="email"
          />
          {!isCreatedEntity && !readOnly && isDirtyFieldBookingEmail && (
            <CheckboxField
              id="isEmailAppliedOnAllOffers"
              label="Utiliser cet email pour me notifier des réservations de toutes les offres déjà postées dans ce lieu."
              labelAligned
              name="isEmailAppliedOnAllOffers"
              readOnly
            />
          )}

          {!venueIsVirtual && (
            <TextareaField
              label="Commentaire (si pas de SIRET) : "
              name="comment"
              readOnly={readOnly}
              rows={1}
              validate={this.commentValidate}
            />
          )}
          <div
            className={classnames('field field-select is-label-aligned', {
              readonly: readOnly,
            })}
          >
            <div className="field-label">
              <label htmlFor="venue-type">Type de lieu : </label>
              <span className="field-asterisk">*</span>
            </div>

            <div className="field-control">
              {readOnly ? (
                <div className="venue-type-label" id="venue-type">
                  <span>
                    {venueIsVirtual ? 'Offre numérique' : venueTypeLabel}
                  </span>
                </div>
              ) : (
                <div className="control control-select">
                  <div className="select">
                    <Field
                      component="select"
                      id="venue-type"
                      name="venueTypeCode"
                      required
                      validate={this.venueTypeValidate}
                    >
                      <option value="">
                        Choisissez un type de lieu dans la liste
                      </option>
                      {venueTypesWithoutVirtualOffer.map(venueType => (
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
              )}
            </div>
          </div>
          {!venueIsVirtual && (
            <div
              className={classnames('field field-select is-label-aligned', {
                readonly: readOnly,
              })}
            >
              <div className="field-label">
                <label htmlFor="venue-label">
                  Label du Ministère de la Culture ou du CNC
                </label>
              </div>

              <div className="field-control">
                {readOnly ? (
                  <div className="venue-label-label" id="venue-label">
                    <span>{venueLabelText}</span>
                  </div>
                ) : (
                  <div className="control control-select">
                    <div className="select">
                      <Field
                        component="select"
                        id="venue-label"
                        name="venueLabelId"
                      >
                        <option value="">
                          Si votre lieu est labellisé précisez-le en le
                          sélectionnant dans la liste
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
                )}
              </div>
            </div>
          )}
          {!venueIsVirtual && (
            <TextareaField
              label="Description : "
              name="description"
              readOnly={readOnly}
            />
          )}
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
  isDirtyFieldBookingEmail: false,
  readOnly: true,
  venueIsVirtual: false,
  venueLabelId: null,
  venueTypeCode: null,
}

IdentifierFields.propTypes = {
  fieldReadOnlyBecauseFrozenFormSiret: PropTypes.bool,
  formSiret: PropTypes.string,
  initialSiret: PropTypes.string,
  isCreatedEntity: PropTypes.bool,
  isDirtyFieldBookingEmail: PropTypes.bool,
  readOnly: PropTypes.bool,
  venueIsVirtual: PropTypes.bool,
  venueLabelId: PropTypes.string,
  venueLabels: PropTypes.arrayOf(PropTypes.instanceOf(VenueLabel)).isRequired,
  venueTypeCode: PropTypes.string,
  venueTypes: PropTypes.arrayOf(PropTypes.instanceOf(VenueType)).isRequired,
}

export default IdentifierFields
