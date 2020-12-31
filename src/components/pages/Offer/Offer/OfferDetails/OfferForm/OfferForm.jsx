import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState, useRef } from 'react'

import { CheckboxInput } from 'components/layout/inputs/CheckboxInput/CheckboxInput'
import DurationInput from 'components/layout/inputs/DurationInput/DurationInput'
import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import TextareaInput from 'components/layout/inputs/TextareaInput'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import Spinner from 'components/layout/Spinner'
import { isAllocineOffer, isSynchronizedOffer } from 'components/pages/Offer/domain/localProvider'
import offerIsRefundable from 'components/pages/Offer/domain/offerIsRefundable'
import * as pcapi from 'repository/pcapi/pcapi'

import SynchronizedProviderInformation from '../SynchronizedProviderInformation'

import {
  BASE_OFFER_FIELDS,
  DEFAULT_FORM_VALUES,
  EDITED_OFFER_READ_ONLY_FIELDS,
  EXTRA_DATA_FIELDS,
  MANDATORY_FIELDS,
} from './_constants'
import OfferRefundWarning from './OfferRefundWarning'
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
  initialValues,
  isUserAdmin,
  offer,
  onSubmit,
  showErrorNotification,
  setShowThumbnailForm,
  submitErrors,
}) => {
  const [formValues, setFormValues] = useState({})
  const [offerType, setOfferType] = useState(null)
  const [receiveNotificationEmails, setReceiveNotificationEmails] = useState(false)
  const [types, setTypes] = useState([])
  const [venue, setVenue] = useState(null)
  const [venueOptions, setVenueOptions] = useState([])
  const [offerFormFields, setOfferFormFields] = useState(Object.keys(DEFAULT_FORM_VALUES))
  const [formErrors, setFormErrors] = useState(submitErrors)
  const isBusy = useRef(true)
  const offererOptions = useRef([])
  const readOnlyFields = useRef([])
  const venues = useRef([])

  const handleFormUpdate = useCallback(
    newFormValues => setFormValues(oldFormValues => ({ ...oldFormValues, ...newFormValues })),
    [setFormValues]
  )

  useEffect(() => {
    setFormErrors(submitErrors)
  }, [submitErrors])
  useEffect(
    function retrieveDataOnMount() {
      pcapi.loadTypes().then(receivedTypes => setTypes(receivedTypes))
      pcapi
        .getValidatedOfferers()
        .then(offerers => buildSelectOptions('id', 'name', offerers))
        .then(options => {
          offererOptions.current = options
          if (options.length === 1) {
            handleFormUpdate({ offererId: options[0].id })
          }
        })
    },
    [handleFormUpdate]
  )
  useEffect(
    function initializeFormData() {
      let values
      if (offer) {
        values = Object.keys(DEFAULT_FORM_VALUES).reduce((acc, field) => {
          if (field in offer && offer[field] !== null) {
            return { ...acc, [field]: offer[field] }
          } else if (offer.extraData && field in offer.extraData) {
            return { ...acc, [field]: offer.extraData[field] }
          }
          return { ...acc, [field]: DEFAULT_FORM_VALUES[field] }
        }, {})

        if (offer.venue) {
          // FIXME (rlecellier): what happend if this offerer isn't
          // in the 10 offerers received by getValidatedOfferers() ?!
          values.offererId = offer.venue.managingOffererId
        }

        const isOfferSynchronized = isSynchronizedOffer(offer)
        if (isOfferSynchronized) {
          let synchonizedOfferReadOnlyFields = Object.keys(DEFAULT_FORM_VALUES)
          if (isAllocineOffer(offer)) {
            synchonizedOfferReadOnlyFields = synchonizedOfferReadOnlyFields.filter(
              fieldName => fieldName !== 'isDuo'
            )
          }
          readOnlyFields.current = synchonizedOfferReadOnlyFields
        } else {
          readOnlyFields.current = EDITED_OFFER_READ_ONLY_FIELDS
        }
        if (offer.bookingEmail !== null) {
          setReceiveNotificationEmails(true)
        }
      } else {
        values = { ...DEFAULT_FORM_VALUES, ...initialValues }
      }

      setFormValues(values)
      isBusy.current = false
    },
    [initialValues, offer]
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
        setVenue(venues.current.find(venue => venue.id === formValues.venueId))
      } else {
        setVenue(null)
      }
    },
    [formValues.type, formValues.venueId, venueOptions, types]
  )
  useEffect(
    function selectManagingOffererOfSelectedVenue() {
      if (venue) {
        handleFormUpdate({ offererId: venue.managingOffererId })
      }
    },
    [handleFormUpdate, venue]
  )
  useEffect(
    function retrieveVenuesOfSelectedOfferer() {
      let offererId = formValues.offererId
      if (offererId === DEFAULT_FORM_VALUES.offererId) {
        offererId = null
      }

      if (!isUserAdmin || offererId) {
        pcapi.getVenuesForOfferer(offererId).then(receivedVenues => {
          venues.current = receivedVenues
        })
      }
    },
    [formValues.offererId, isUserAdmin]
  )
  useEffect(
    function filterVenueOptionsForSelectedType() {
      let venuesToShow = venues.current
      if (offerType?.offlineOnly) {
        venuesToShow = venuesToShow.filter(venue => !venue.isVirtual)
      } else if (offerType?.onlineOnly) {
        venuesToShow = venuesToShow.filter(venue => venue.isVirtual)
      }
      setVenueOptions(buildSelectOptions('id', 'name', venuesToShow))

      if (venuesToShow.length === 0 && venues.current.length > 0) {
        setFormErrors({ venueId: 'Il faut obligatoirement une structure avec un lieu.' })
      } else {
        setFormErrors({})
      }

      if (venuesToShow.length === 1) {
        handleFormUpdate({ venueId: venuesToShow[0].id })
      }
    },
    [offerType, handleFormUpdate]
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
      const editableFields = offerFormFields.filter(
        field => !readOnlyFields.current.includes(field)
      )
      const submittedValues = editableFields.reduce(
        (submittedValues, fieldName) => {
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
        },
        { extraData: null }
      )

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

  const submitFormButtonText = offer ? 'Enregistrer' : 'Enregistrer et passer au stocks'
  const displayFullForm = offer ? true : formValues.type !== DEFAULT_FORM_VALUES.type
  setShowThumbnailForm(displayFullForm)

  if (isBusy.current) {
    return <Spinner />
  }

  return (
    <form className="offer-form">
      {isSynchronizedOffer(offer) ? (
        <div className="form-row">
          <SynchronizedProviderInformation providerName={offer.lastProvider.name} />
        </div>
      ) : (
        <p className="page-subtitle">
          {'Tous les champs sont obligatoires sauf mention contraire'}
        </p>
      )}

      <section className="form-section">
        <h3 className="section-title">
          {"Type d'offre"}
        </h3>
        <p className="section-description">
          {
            'Le type de l’offre permet de la caractériser au mieux et de la valoriser au mieux dans l’application.'
          }
        </p>

        <div className="form-row">
          <TypeTreeSelects
            isReadOnly={readOnlyFields.current.includes('type')}
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

      {displayFullForm && (
        <Fragment>
          <section className="form-section">
            <h3 className="section-title">
              {'Infos artistiques'}
            </h3>

            <div className="form-row">
              <TextInput
                disabled={readOnlyFields.current.includes('name')}
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
                disabled={readOnlyFields.current.includes('description')}
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
                  disabled={readOnlyFields.current.includes('speaker')}
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
                  disabled={readOnlyFields.current.includes('author')}
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
                  disabled={readOnlyFields.current.includes('visa')}
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
                  disabled={readOnlyFields.current.includes('isbn')}
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
                  disabled={readOnlyFields.current.includes('stageDirector')}
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
                  disabled={readOnlyFields.current.includes('performer')}
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
                  disabled={readOnlyFields.current.includes('durationMinutes')}
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

            <div className="form-row">
              <Select
                defaultOption={{
                  displayName: 'Sélectionnez une structure',
                  id: DEFAULT_FORM_VALUES.offererId,
                }}
                error={getErrorMessage('offererId')}
                handleSelection={handleSingleFormUpdate}
                isDisabled={readOnlyFields.current.includes('offererId')}
                label="Structure"
                name="offererId"
                options={offererOptions.current}
                selectedValue={formValues.offererId}
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
                isDisabled={readOnlyFields.current.includes('venueId')}
                label="Lieu"
                name="venueId"
                options={venueOptions}
                selectedValue={formValues.venueId}
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
                disabled={readOnlyFields.current.includes('withdrawalDetails')}
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
                  disabled={readOnlyFields.current.includes('url')}
                  error={getErrorMessage('url')}
                  label="URL"
                  name="url"
                  onChange={handleSingleFormUpdate}
                  required
                  subLabel={
                    readOnlyFields.current.includes('url')
                      ? 'Vous pouvez inclure {token} {email} et {offerId} dans l’URL, qui seront remplacés respectivement par le code de la contremarque, l’e-mail de la personne ayant reservé et l’identifiant de l’offre'
                      : null
                  }
                  type="text"
                  value={formValues.url}
                />
              </div>
            )}
          </section>

          <section className="form-section">
            <h3 className="section-title">
              {'Autre'}
            </h3>

            {offerFormFields.includes('isNational') && (
              <div className="form-row">
                <CheckboxInput
                  checked={!!formValues.isNational}
                  disabled={readOnlyFields.current.includes('isNational') ? 'disabled' : ''}
                  label="Rayonnement national"
                  name="isNational"
                  onChange={handleSingleFormUpdate}
                />
              </div>
            )}
            {offerFormFields.includes('isDuo') && (
              <div className="form-row">
                <CheckboxInput
                  checked={formValues.isDuo}
                  disabled={readOnlyFields.current.includes('isDuo') ? 'disabled' : ''}
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
                disabled={readOnlyFields.current.includes('bookingEmail')}
                label="Recevoir les emails de réservation"
                name="receiveNotificationEmails"
                onChange={toggleReceiveNotification}
              />
            </div>

            {offerFormFields.includes('bookingEmail') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.current.includes('bookingEmail')}
                  error={getErrorMessage('bookingEmail')}
                  label="Être notifié par email des réservations à :"
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
        {offer ? (
          <button
            className="secondary-button"
            type="button"
          >
            {'Annuler'}
          </button>
        ) : null}
        <button
          className="primary-button"
          onClick={submitForm}
          type="button"
        >
          {submitFormButtonText}
        </button>
      </section>
    </form>
  )
}

OfferForm.defaultProps = {
  initialValues: {},
  isUserAdmin: false,
  offer: null,
}

OfferForm.propTypes = {
  initialValues: PropTypes.shape(),
  isUserAdmin: PropTypes.bool,
  offer: PropTypes.shape(),
  onSubmit: PropTypes.func.isRequired,
  setShowThumbnailForm: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitErrors: PropTypes.shape().isRequired,
}

export default OfferForm
