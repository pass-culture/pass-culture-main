import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import { CheckboxInput } from 'components/layout/inputs/CheckboxInput/CheckboxInput'
import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import TextareaInput from 'components/layout/inputs/TextareaInput'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import TimeInput from 'components/layout/inputs/TimeInput'
import Spinner from 'components/layout/Spinner'
import { isAllocineOffer, isSynchronizedOffer } from 'components/pages/Offer/domain/localProvider'
import offerIsRefundable from 'components/pages/Offer/domain/offerIsRefundable'
import * as pcapi from 'repository/pcapi/pcapi'

import { DEFAULT_FORM_VALUES, MANDATORY_FIELDS } from './_constants'
import OfferRefundWarning from './OfferRefundWarning'
import SynchronizableProviderInformation from './SynchronizableProviderInformation'
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
  submitErrors,
}) => {
  const [formValues, setFormValues] = useState({})
  const [offererOptions, setOffererOptions] = useState([])
  const [offerType, setOfferType] = useState(null)
  const [receiveNotificationEmails, setReceiveNotificationEmails] = useState(false)
  const [types, setTypes] = useState([])
  const [venue, setVenue] = useState(null)
  const [venues, setVenues] = useState([])
  const [venueOptions, setVenueOptions] = useState([])
  const [offerIsSynchronized, setOfferIsSynchronized] = useState(false)
  const [offerFormFields, setOfferFormFields] = useState(Object.keys(DEFAULT_FORM_VALUES))
  const [readOnlyFields, setReadOnlyFields] = useState([''])
  const [formErrors, setFormErrors] = useState(submitErrors)
  const [isBusy, setIsBusy] = useState(true)

  const handleFormUpdate = useCallback(
    newFormValues => setFormValues(oldFormValues => ({ ...oldFormValues, ...newFormValues })),
    [setFormValues]
  )

  useEffect(() => {
    setFormErrors(submitErrors)
  }, [submitErrors])
  useEffect(function retrieveDataOnMount() {
    pcapi.loadTypes().then(receivedTypes => setTypes(receivedTypes))
    pcapi
      .getValidatedOfferers()
      .then(offerers => buildSelectOptions('id', 'name', offerers))
      .then(offererOptions => setOffererOptions(offererOptions))
  }, [])
  useEffect(
    function selectOffererOrVenueWhenUnique() {
      if (offererOptions.length === 1) {
        handleFormUpdate({ offererId: offererOptions[0].id })
      }
      if (venueOptions.length === 1) {
        handleFormUpdate({ venueId: venueOptions[0].id })
      }
    },
    [handleFormUpdate, offererOptions, venueOptions]
  )
  useEffect(
    function initializeFormData() {
      let values = {}
      if (offer) {
        values = Object.keys(DEFAULT_FORM_VALUES).reduce((acc, field) => {
          if (offer[field]) {
            return { ...acc, [field]: offer[field] }
          } else if (offer.extraData && field in offer.extraData) {
            return { ...acc, [field]: offer.extraData[field] || DEFAULT_FORM_VALUES[field] }
          }
          return { ...acc, [field]: DEFAULT_FORM_VALUES[field] }
        }, {})

        if (offer.venue) {
          // FIXME (rlecellier): what happend if this offerer isn't
          // in the 10 offerers received by getValidatedOfferers() ?!
          values.offererId = offer.venue.managingOffererId
        }

        const isSynchronized = isSynchronizedOffer(offer)
        setOfferIsSynchronized(isSynchronized)
        if (isSynchronized) {
          let syncReadOnlyFields = Object.keys(DEFAULT_FORM_VALUES)
          if (isAllocineOffer(offer)) {
            syncReadOnlyFields = syncReadOnlyFields.filter(fieldName => fieldName !== 'isDuo')
          }
          setReadOnlyFields(syncReadOnlyFields)
        } else {
          setReadOnlyFields([
            'type',
            'musicType',
            'musicSubType',
            'offererId',
            'showType',
            'showSubType',
          ])
        }
        if (offer.bookingEmail && offer.bookingEmail.length) {
          setReceiveNotificationEmails(true)
        }
      } else {
        values = { ...DEFAULT_FORM_VALUES, ...initialValues }
      }

      setFormValues(values)
      setIsBusy(false)
    },
    [initialValues, offer]
  )
  useEffect(
    function buildFormFields() {
      const baseOfferFields = ['description', 'name', 'type', 'venueId', 'withdrawalDetails']

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
        ...baseOfferFields,
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
        setVenue(venues.find(venue => venue.id === formValues.venueId))
      } else {
        setVenue(null)
      }
    },
    [formValues.type, formValues.venueId, venueOptions, types, venues]
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
          setVenues(receivedVenues)
        })
      }
    },
    [formValues.offererId, isUserAdmin]
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
        setFormErrors({ venueId: 'Il faut obligatoirement une structure avec un lieu.' })
      } else {
        setFormErrors({})
      }
    },
    [offerType, venues]
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
      const extraDataFields = [
        'author',
        'isbn',
        'musicType',
        'musicSubType',
        'performer',
        'showType',
        'showSubType',
        'speaker',
        'visa',
      ]

      const submitedValues = offerFormFields.reduce((acc, fieldName) => {
        if (extraDataFields.includes(fieldName)) {
          if (!('extraData' in acc)) {
            acc.extraData = {}
          }
          acc.extraData[fieldName] = formValues[fieldName]
        } else {
          acc = { ...acc, [fieldName]: formValues[fieldName] }
        }
        return acc
      }, {})

      if (!receiveNotificationEmails) {
        submitedValues.bookingEmail = null
      }

      onSubmit(submitedValues)
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
      const checkboxFields = ['isDuo', 'isNational', 'receiveNotificationEmails']
      const field = event.target.name
      const value = checkboxFields.includes(field) ? !formValues[field] : event.target.value
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

  let submitFormButtonText = 'Enregistrer'
  let displayFullForm = true

  if (!offer) {
    submitFormButtonText = 'Enregistrer et passer au stocks'
    displayFullForm = !!formValues.type
  }

  if (isBusy) {
    return <Spinner />
  }

  return (
    <form className="offer-form">
      <section className="form-section">
        <h3 className="section-title">
          {"Type d'offre"}
        </h3>
        <p className="section-description">
          {
            'La catégorie de l’offre permet de la caractériser au mieux et de la valoriser au mieux dans l’application.'
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

        {offerIsSynchronized && (
          <div className="form-row">
            <SynchronizableProviderInformation offer={offer} />
          </div>
        )}
      </section>

      {displayFullForm && (
        <Fragment>
          <section className="form-section">
            <h3 className="section-title">
              {'Infos artistiques'}
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
                required
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
                <TimeInput
                  error={getErrorMessage('durationMinutes')}
                  label="Durée"
                  name="durationMinutes"
                  onChange={handleDurationChange}
                  placeholder="HH:MM"
                  readOnly={readOnlyFields.includes('durationMinutes')}
                  subLabel={!MANDATORY_FIELDS.includes('durationMinutes') ? 'Optionnel' : ''}
                  type="duration"
                  value={formValues.durationMinutes}
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
                isDisabled={readOnlyFields.includes('offererId')}
                label="Structure"
                name="offererId"
                options={offererOptions}
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
                isDisabled={readOnlyFields.includes('venueId')}
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
                disabled={readOnlyFields.includes('withdrawalDetails')}
                error={getErrorMessage('withdrawalDetails')}
                label="Informations de retrait"
                maxLength={500}
                name="withdrawalDetails"
                onChange={handleSingleFormUpdate}
                required
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
                    !readOnlyFields.includes('url') &&
                    'Vous pouvez inclure {token} {email} et {offerId} dans l’URL, qui seront remplacés respectivement par le code de la contremarque, l’e-mail de la personne ayant reservé et l’identifiant de l’offre'
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
                  checked={formValues.isDuo}
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
                label="Recevoir les emails de réservation"
                name="receiveNotificationEmails"
                onChange={toggleReceiveNotification}
              />
            </div>

            {offerFormFields.includes('bookingEmail') && (
              <div className="form-row">
                <TextInput
                  disabled={readOnlyFields.includes('bookingEmail')}
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
  showErrorNotification: PropTypes.func.isRequired,
}

export default OfferForm
