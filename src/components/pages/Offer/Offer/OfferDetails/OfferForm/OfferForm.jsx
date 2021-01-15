import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import { CheckboxInput } from 'components/layout/inputs/CheckboxInput/CheckboxInput'
import DurationInput from 'components/layout/inputs/DurationInput/DurationInput'
import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import TextareaInput from 'components/layout/inputs/TextareaInput'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import offerIsRefundable from 'components/pages/Offer/domain/offerIsRefundable'

import SynchronizedProviderInformation from '../SynchronizedProviderInformation'

import {
  BASE_OFFER_FIELDS,
  DEFAULT_FORM_VALUES,
  EXTRA_DATA_FIELDS,
  MANDATORY_FIELDS,
} from './_constants'
import { ReactComponent as AudioDisabilitySvg } from './assets/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from './assets/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from './assets/motor-disability.svg'
import { ReactComponent as VisualDisabilitySvg } from './assets/visual-disability.svg'
import OfferRefundWarning from './Messages/OfferRefundWarning'
import WithdrawalReminder from './Messages/WithdrawalReminder'
import TypeTreeSelects from './TypeTreeSelects'

const getOfferConditionalFields = ({
  offerType = null,
  isUserAdmin = null,
  receiveNotificationEmails = null,
  venue = null,
}) => {
  let offerConditionalFields = []

  if (offerType && offerType.type === 'Event') {
    offerConditionalFields.push('durationMinutes')
    offerConditionalFields.push('isDuo')
  }

  if (isUserAdmin) {
    offerConditionalFields.push('isNational')
  }

  if (receiveNotificationEmails) {
    offerConditionalFields.push('bookingEmail')
  }

  if (venue && venue.isVirtual) {
    offerConditionalFields.push('url')
  }

  return offerConditionalFields
}

const OfferForm = ({
  backUrl,
  initialValues,
  isEdition,
  isUserAdmin,
  offerers,
  onSubmit,
  providerName,
  readOnlyFields,
  setSelectedOfferer,
  setShowThumbnailForm,
  showErrorNotification,
  submitErrors,
  types,
  venues,
}) => {
  const [formValues, setFormValues] = useState({})
  const [offerType, setOfferType] = useState(null)
  const [receiveNotificationEmails, setReceiveNotificationEmails] = useState(false)
  const [venue, setVenue] = useState(null)
  const [venueOptions, setVenueOptions] = useState(buildSelectOptions('id', 'name', venues))
  const [offerFormFields, setOfferFormFields] = useState(Object.keys(DEFAULT_FORM_VALUES))
  const [formErrors, setFormErrors] = useState(submitErrors)

  const handleFormUpdate = useCallback(
    newFormValues => setFormValues(oldFormValues => ({ ...oldFormValues, ...newFormValues })),
    [setFormValues]
  )
  const offererOptions = buildSelectOptions('id', 'name', offerers)

  useEffect(() => {
    setFormErrors(submitErrors)
  }, [submitErrors])
  useEffect(
    function initializeFormData() {
      if (
        initialValues.bookingEmail &&
        initialValues.bookingEmail !== DEFAULT_FORM_VALUES.bookingEmail
      ) {
        setReceiveNotificationEmails(true)
      }
      setFormValues({ ...DEFAULT_FORM_VALUES, ...initialValues })
    },
    [initialValues]
  )
  useEffect(
    function buildFormFields() {
      const offerConditionalFields = getOfferConditionalFields({
        offerType,
        isUserAdmin,
        receiveNotificationEmails,
        venue,
      })
      let offerTypeConditionalFields = offerType ? offerType.conditionalFields : []
      if (offerTypeConditionalFields.includes('musicType')) {
        offerTypeConditionalFields.push('musicSubType')
      }
      if (offerTypeConditionalFields.includes('showType')) {
        offerTypeConditionalFields.push('showSubType')
      }

      const newFormFields = [
        ...BASE_OFFER_FIELDS,
        ...offerTypeConditionalFields,
        ...offerConditionalFields,
      ]

      setOfferFormFields(newFormFields)
    },
    [offerType, isUserAdmin, receiveNotificationEmails, venue]
  )
  useEffect(
    function storeOfferTypeAndVenueWhenSelected() {
      if (formValues.type) {
        setOfferType(types.find(type => type.value === formValues.type))
      }

      if (
        formValues.venueId &&
        venueOptions.find(showedVenue => showedVenue.id === formValues.venueId)
      ) {
        const selectedVenue = venues.find(venue => venue.id === formValues.venueId)
        setVenue(selectedVenue)
        handleFormUpdate({ offererId: selectedVenue.managingOffererId })
      } else {
        setVenue(null)
      }
    },
    [formValues.type, formValues.venueId, handleFormUpdate, venues, venueOptions, types]
  )
  useEffect(
    function filterVenueOptionsForSelectedType() {
      let venuesToShow = venues
      if (offerType?.offlineOnly) {
        venuesToShow = venuesToShow.filter(venue => !venue.isVirtual)
      } else if (offerType?.onlineOnly) {
        venuesToShow = venuesToShow.filter(venue => venue.isVirtual)
      }
      setVenueOptions(buildSelectOptions('id', 'name', venuesToShow))

      if (venuesToShow.length === 0 && venues.length > 0) {
        setFormErrors(oldFormErrors => ({
          ...oldFormErrors,
          venueId: 'Il faut obligatoirement une structure avec un lieu.',
        }))
      } else {
        setFormErrors(oldFormErrors => {
          delete oldFormErrors.venueId
          return oldFormErrors
        })
      }

      if (venuesToShow.length === 1) {
        handleFormUpdate({ venueId: venuesToShow[0].id })
      }
    },
    [offerType, handleFormUpdate, venues]
  )
  useEffect(
    function selectOffererWhenUnique() {
      if (offerers.length === 1) {
        handleFormUpdate({ offererId: offerers[0].id })
      }
    },
    [handleFormUpdate, offerers]
  )
  useEffect(
    function showThumbnail() {
      setShowThumbnailForm(formValues.type !== DEFAULT_FORM_VALUES.type)
    },
    [formValues.type, setShowThumbnailForm]
  )

  const selectOfferer = useCallback(
    event => {
      const selectedOffererId = event.target.value
      if (selectedOffererId !== formValues.offererId) {
        handleFormUpdate({ offererId: selectedOffererId, venueId: DEFAULT_FORM_VALUES.venueId })
        setSelectedOfferer(selectedOffererId)
      }
    },
    [formValues.offererId, handleFormUpdate, setSelectedOfferer]
  )

  const isValid = useCallback(() => {
    let newFormErrors = {}
    const formFields = [...offerFormFields, 'offererId']

    MANDATORY_FIELDS.forEach(fieldName => {
      if (
        formFields.includes(fieldName) &&
        formValues[fieldName] === DEFAULT_FORM_VALUES[fieldName]
      ) {
        newFormErrors[fieldName] = 'Ce champ est obligatoire.'
      }
    })

    setFormErrors(newFormErrors)
    return Object.keys(newFormErrors).length === 0
  }, [offerFormFields, formValues])

  const submitForm = useCallback(() => {
    if (isValid()) {
      const editableFields = offerFormFields.filter(field => !readOnlyFields.includes(field))
      const submittedValuesAccumulator = editableFields.some(editableField =>
        EXTRA_DATA_FIELDS.includes(editableField)
      )
        ? { extraData: null }
        : {}
      const submittedValues = editableFields.reduce((submittedValues, fieldName) => {
        if (!EXTRA_DATA_FIELDS.includes(fieldName)) {
          submittedValues = {
            ...submittedValues,
            [fieldName]: formValues[fieldName],
          }
        } else if (formValues[fieldName] !== DEFAULT_FORM_VALUES[fieldName]) {
          submittedValues.extraData = {
            ...submittedValues.extraData,
            [fieldName]: formValues[fieldName],
          }
        }
        return submittedValues
      }, submittedValuesAccumulator)

      if (!receiveNotificationEmails) {
        submittedValues.bookingEmail = null
      }

      onSubmit(submittedValues)
    } else {
      showErrorNotification()
    }
  }, [
    offerFormFields,
    formValues,
    isValid,
    onSubmit,
    readOnlyFields,
    receiveNotificationEmails,
    showErrorNotification,
  ])

  const handleSingleFormUpdate = useCallback(
    event => {
      const field = event.target.name
      const value = event.target.type === 'checkbox' ? !formValues[field] : event.target.value
      handleFormUpdate({ [field]: value })
    },
    [formValues, handleFormUpdate]
  )

  const handleDurationChange = useCallback(value => handleFormUpdate({ durationMinutes: value }), [
    handleFormUpdate,
  ])

  // TODO rlecellier: see if it can be moved in offer default value (as offerer)
  const toggleReceiveNotification = useCallback(
    () => setReceiveNotificationEmails(!receiveNotificationEmails),
    [setReceiveNotificationEmails, receiveNotificationEmails]
  )

  const displayRefundWarning = !offerIsRefundable(offerType, venue)

  const getErrorMessage = fieldName => {
    return fieldName in formErrors ? formErrors[fieldName] : null
  }

  return (
    <form className="offer-form">
      {providerName !== null ? (
        <SynchronizedProviderInformation providerName={providerName} />
      ) : (
        <p className="page-subtitle">
          {'Tous les champs sont obligatoires sauf mention contraire.'}
        </p>
      )}

      <section className="form-section">
        <h3 className="section-title">
          {"Type d'offre"}
        </h3>
        <p className="section-description">
          {
            'Le type de l’offre permet de la caractériser et de la valoriser au mieux dans l’application.'
          }
        </p>

        <div className="form-row">
          <TypeTreeSelects
            isReadOnly={readOnlyFields.includes('type')}
            typeValues={{
              type: formValues.type,
              musicType: formValues.musicType,
              musicSubType: formValues.musicSubType,
              showType: formValues.showType,
              showSubType: formValues.showSubType,
            }}
            types={types}
            updateTypeValues={handleFormUpdate}
          />
        </div>
      </section>

      {formValues.type !== DEFAULT_FORM_VALUES.type && (
        <Fragment>
          <section className="form-section">
            <h3 className="section-title">
              {'Informations artistiques'}
            </h3>

            <div className="form-row">
              <TextInput
                disabled={readOnlyFields.includes('name')}
                error={getErrorMessage('name')}
                label="Titre de l'offre"
                name="name"
                onChange={handleSingleFormUpdate}
                required
                subLabel={!MANDATORY_FIELDS.includes('name') ? 'Optionnel' : ''}
                type="text"
                value={formValues.name}
              />
            </div>
            <div className="form-row">
              <TextareaInput
                countCharacters
                disabled={readOnlyFields.includes('description')}
                error={getErrorMessage('description')}
                label="Description"
                maxLength={1000}
                name="description"
                onChange={handleSingleFormUpdate}
                rows={6}
                subLabel={!MANDATORY_FIELDS.includes('description') ? 'Optionnel' : ''}
                value={formValues.description}
              />
            </div>
            {offerFormFields.includes('speaker') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('speaker')}
                  error={getErrorMessage('speaker')}
                  label="Intervenant"
                  name="speaker"
                  onChange={handleSingleFormUpdate}
                  subLabel={!MANDATORY_FIELDS.includes('speaker') ? 'Optionnel' : ''}
                  type="text"
                  value={formValues.speaker}
                />
              </div>
            )}

            {offerFormFields.includes('author') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('author')}
                  error={getErrorMessage('author')}
                  label="Auteur"
                  name="author"
                  onChange={handleSingleFormUpdate}
                  subLabel={!MANDATORY_FIELDS.includes('author') ? 'Optionnel' : ''}
                  type="text"
                  value={formValues.author}
                />
              </div>
            )}

            {offerFormFields.includes('visa') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('visa')}
                  error={getErrorMessage('visa')}
                  label="Visa d’exploitation"
                  name="visa"
                  onChange={handleSingleFormUpdate}
                  subLabel={!MANDATORY_FIELDS.includes('visa') ? 'Optionnel' : ''}
                  type="text"
                  value={formValues.visa}
                />
              </div>
            )}

            {offerFormFields.includes('isbn') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('isbn')}
                  error={getErrorMessage('isbn')}
                  label="ISBN"
                  name="isbn"
                  onChange={handleSingleFormUpdate}
                  subLabel={!MANDATORY_FIELDS.includes('isbn') ? 'Optionnel' : ''}
                  type="text"
                  value={formValues.isbn}
                />
              </div>
            )}

            {offerFormFields.includes('stageDirector') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('stageDirector')}
                  error={getErrorMessage('stageDirector')}
                  label="Metteur en scène"
                  name="stageDirector"
                  onChange={handleSingleFormUpdate}
                  subLabel={!MANDATORY_FIELDS.includes('stageDirector') ? 'Optionnel' : ''}
                  type="text"
                  value={formValues.stageDirector}
                />
              </div>
            )}

            {offerFormFields.includes('performer') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('performer')}
                  error={getErrorMessage('perforer')}
                  label="Interprète"
                  name="performer"
                  onChange={handleSingleFormUpdate}
                  subLabel={!MANDATORY_FIELDS.includes('performer') ? 'Optionnel' : ''}
                  type="text"
                  value={formValues.performer}
                />
              </div>
            )}

            {offerFormFields.includes('durationMinutes') && (
              <div className="form-row">
                <DurationInput
                  disabled={readOnlyFields.includes('durationMinutes')}
                  error={getErrorMessage('durationMinutes')}
                  initialDurationInMinutes={formValues.durationMinutes}
                  label="Durée"
                  name="durationMinutes"
                  onChange={handleDurationChange}
                  placeholder="HH:MM"
                  subLabel={!MANDATORY_FIELDS.includes('durationMinutes') ? 'Optionnel' : ''}
                />
              </div>
            )}
          </section>

          <section className="form-section">
            <h3 className="section-title">
              {'Informations pratiques'}
            </h3>
            <p className="section-description">
              {
                'Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande.'
              }
            </p>

            {offerType?.type === 'Thing' && venue && !venue.isVirtual && <WithdrawalReminder />}

            <div className="form-row">
              <Select
                defaultOption={{
                  displayName: 'Sélectionnez une structure',
                  id: DEFAULT_FORM_VALUES.offererId,
                }}
                error={getErrorMessage('offererId')}
                handleSelection={selectOfferer}
                isDisabled={readOnlyFields.includes('offererId')}
                label="Structure"
                name="offererId"
                options={offererOptions}
                selectedValue={formValues.offererId || DEFAULT_FORM_VALUES.offererId}
                subLabel={!MANDATORY_FIELDS.includes('offererId') ? 'Optionnel' : ''}
              />
            </div>

            <div className="form-row">
              <Select
                defaultOption={{
                  displayName: 'Sélectionnez un lieu',
                  id: DEFAULT_FORM_VALUES.venueId,
                }}
                error={getErrorMessage('venueId')}
                handleSelection={handleSingleFormUpdate}
                isDisabled={readOnlyFields.includes('venueId')}
                label="Lieu"
                name="venueId"
                options={venueOptions}
                selectedValue={formValues.venueId || DEFAULT_FORM_VALUES.venueId}
                subLabel={!MANDATORY_FIELDS.includes('venueId') ? 'Optionnel' : ''}
              />
            </div>
            {displayRefundWarning && (
              <div className="form-row">
                <OfferRefundWarning />
              </div>
            )}

            <div className="form-row">
              <TextareaInput
                countCharacters
                disabled={readOnlyFields.includes('withdrawalDetails')}
                error={getErrorMessage('withdrawalDetails')}
                label="Informations de retrait"
                maxLength={500}
                name="withdrawalDetails"
                onChange={handleSingleFormUpdate}
                rows={6}
                subLabel={!MANDATORY_FIELDS.includes('withdrawalDetails') ? 'Optionnel' : ''}
                value={formValues.withdrawalDetails}
              />
            </div>

            {offerFormFields.includes('url') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('url')}
                  error={getErrorMessage('url')}
                  label="URL"
                  name="url"
                  onChange={handleSingleFormUpdate}
                  required
                  subLabel={
                    readOnlyFields.includes('url')
                      ? 'Vous pouvez inclure {token} {email} et {offerId} dans l’URL, qui seront remplacés respectivement par le code de la contremarque, l’e-mail de la personne ayant reservé et l’identifiant de l’offre'
                      : null
                  }
                  type="text"
                  value={formValues.url}
                />
              </div>
            )}
          </section>

          <section className="form-section accessibility-section">
            <h3 className="section-title">
              {'Accessibilité'}
            </h3>
            <p className="section-description">
              {'Cette offre est accessible aux publics en situation de :'}
            </p>
            <CheckboxInput
              SvgElement={VisualDisabilitySvg}
              checked={formValues.visualDisabilityCompliant || false}
              label="Handicap visuel"
              name="visualDisabilityCompliant"
              onChange={handleSingleFormUpdate}
            />
            <CheckboxInput
              SvgElement={MentalDisabilitySvg}
              checked={formValues.mentalDisabilityCompliant || false}
              label="Handicap mental"
              name="mentalDisabilityCompliant"
              onChange={handleSingleFormUpdate}
            />
            <CheckboxInput
              SvgElement={MotorDisabilitySvg}
              checked={formValues.motorDisabilityCompliant || false}
              label="Handicap moteur"
              name="motorDisabilityCompliant"
              onChange={handleSingleFormUpdate}
            />
            <CheckboxInput
              SvgElement={AudioDisabilitySvg}
              checked={formValues.audioDisabilityCompliant || false}
              label="Handicap auditif"
              name="audioDisabilityCompliant"
              onChange={handleSingleFormUpdate}
            />
          </section>

          <section className="form-section">
            <h3 className="section-title">
              {'Autre'}
            </h3>

            {offerFormFields.includes('isNational') && (
              <div className="form-row">
                <CheckboxInput
                  checked={formValues.isNational || false}
                  disabled={readOnlyFields.includes('isNational') ? 'disabled' : ''}
                  label="Rayonnement national"
                  name="isNational"
                  onChange={handleSingleFormUpdate}
                />
              </div>
            )}
            {offerFormFields.includes('isDuo') && (
              <div className="form-row">
                <CheckboxInput
                  checked={formValues.isDuo || false}
                  disabled={readOnlyFields.includes('isDuo') ? 'disabled' : ''}
                  label={'Accepter les réservations "duo"'}
                  name="isDuo"
                  onChange={handleSingleFormUpdate}
                  subLabel={
                    "En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l'accompagnateur."
                  }
                />
              </div>
            )}
            <div className="form-row">
              <CheckboxInput
                checked={receiveNotificationEmails}
                disabled={readOnlyFields.includes('bookingEmail')}
                label="Être notifié par email des réservations"
                name="receiveNotificationEmails"
                onChange={toggleReceiveNotification}
              />
            </div>

            {offerFormFields.includes('bookingEmail') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('bookingEmail')}
                  error={getErrorMessage('bookingEmail')}
                  label="Email auquel envoyer les notifications :"
                  name="bookingEmail"
                  onChange={handleSingleFormUpdate}
                  placeholder="adresse@email.com"
                  required
                  type="email"
                  value={formValues.bookingEmail}
                />
              </div>
            )}
          </section>
        </Fragment>
      )}

      <section className="actions-section">
        {isEdition ? (
          <a
            className="secondary-link"
            href={backUrl}
          >
            {'Annuler et quitter'}
          </a>
        ) : null}
        <button
          className="primary-button"
          onClick={submitForm}
          type="button"
        >
          {isEdition ? 'Enregistrer' : 'Enregistrer et passer aux stocks'}
        </button>
      </section>
    </form>
  )
}

OfferForm.defaultProps = {
  backUrl: null,
  initialValues: {},
  isEdition: false,
  isUserAdmin: false,
  providerName: null,
  readOnlyFields: [],
}

OfferForm.propTypes = {
  backUrl: PropTypes.string,
  initialValues: PropTypes.shape(),
  isEdition: PropTypes.bool,
  isUserAdmin: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  providerName: PropTypes.string,
  readOnlyFields: PropTypes.arrayOf(PropTypes.string),
  setShowThumbnailForm: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitErrors: PropTypes.shape().isRequired,
}

export default OfferForm
