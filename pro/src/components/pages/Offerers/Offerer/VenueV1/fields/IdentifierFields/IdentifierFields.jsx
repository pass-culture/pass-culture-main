import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'
import ReactTooltip from 'react-tooltip'

import HiddenField from 'components/layout/form/fields/HiddenField'
import TextareaField from 'components/layout/form/fields/TextareaField'
import TextField from 'components/layout/form/fields/TextField'
import Icon from 'components/layout/Icon'
import VenueLabel from 'components/pages/Offerers/Offerer/VenueV1/ValueObjects/VenueLabel'
import VenueType from 'components/pages/Offerers/Offerer/VenueV1/ValueObjects/VenueType'
import { CheckboxField } from 'ui-kit'

import SiretOrCommentFields from '../SiretOrCommentFields'

/*eslint no-undef: 0*/

import getLabelFromList from './utils/getLabelFromList'

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
      isToggleDisabled,
      readOnly,
      siren,
      updateIsSiretValued,
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
          {!venueIsVirtual && (
            <SiretOrCommentFields
              siretLabel={siretLabel}
              readOnly={readOnly || initialSiret !== null}
              siren={siren}
              isToggleDisabled={isToggleDisabled}
              isCreatedEntity={isCreatedEntity}
              initialSiret={initialSiret}
              updateIsSiretValued={updateIsSiretValued}
            />
          )}
          {isCreatedEntity && <HiddenField name="managingOffererId" />}
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
                  Label du Ministère de la Culture ou du CNC :
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
  isToggleDisabled: false,
  readOnly: true,
  siren: null,
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
  isToggleDisabled: PropTypes.bool,
  readOnly: PropTypes.bool,
  siren: PropTypes.string,
  updateIsSiretValued: PropTypes.func,
  venueIsVirtual: PropTypes.bool,
  venueLabelId: PropTypes.string,
  venueLabels: PropTypes.arrayOf(PropTypes.instanceOf(VenueLabel)).isRequired,
  venueTypeCode: PropTypes.string,
  venueTypes: PropTypes.arrayOf(PropTypes.instanceOf(VenueType)).isRequired,
}

export default IdentifierFields
