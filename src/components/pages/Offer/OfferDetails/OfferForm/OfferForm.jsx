import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import { CheckboxInput } from 'components/layout/inputs/CheckboxInput/CheckboxInput'
import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import TextareaInput from 'components/layout/inputs/TextareaInput'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import TimeInput from 'components/layout/inputs/TimeInput'
import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'

import { isSynchronizedOffer } from '../../domain/localProvider'
import offerIsRefundable from '../../domain/offerIsRefundable'
import MediationsManager from '../../MediationsManager/MediationsManagerContainer'
import { SELECT_DEFAULT_VALUE, TEXT_INPUT_DEFAULT_VALUE } from '../_constants'

import OfferRefundWarning from './OfferRefundWarning'
import SynchronizableProviderInformation from './SynchronizableProviderInformation'
import TypeTreeSelects from './TypeTreeSelects'

export const DEFAULT_FORM_VALUES = {
  author: TEXT_INPUT_DEFAULT_VALUE,
  bookingEmail: TEXT_INPUT_DEFAULT_VALUE,
  description: TEXT_INPUT_DEFAULT_VALUE,
  durationMinutes: TEXT_INPUT_DEFAULT_VALUE,
  isbn: TEXT_INPUT_DEFAULT_VALUE,
  isDuo: false,
  isNational: false,
  name: TEXT_INPUT_DEFAULT_VALUE,
  musicSubType: SELECT_DEFAULT_VALUE,
  musicType: SELECT_DEFAULT_VALUE,
  offererId: SELECT_DEFAULT_VALUE,
  performer: TEXT_INPUT_DEFAULT_VALUE,
  showSubType: SELECT_DEFAULT_VALUE,
  showType: SELECT_DEFAULT_VALUE,
  stageDirector: TEXT_INPUT_DEFAULT_VALUE,
  speaker: TEXT_INPUT_DEFAULT_VALUE,
  type: SELECT_DEFAULT_VALUE,
  url: TEXT_INPUT_DEFAULT_VALUE,
  venueId: SELECT_DEFAULT_VALUE,
  visa: TEXT_INPUT_DEFAULT_VALUE,
  withdrawalDetails: TEXT_INPUT_DEFAULT_VALUE,
}

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

const OfferForm = props => {
  const { offer, initialValues, onSubmit, onChange, isUserAdmin, submitErrors } = props

  const [formValues, setFormValues] = useState({})
  const [offererOptions, setOffererOptions] = useState([])
  const [offerType, setOfferType] = useState(null)
  const [receiveNotificationEmails, setReceiveNotificationEmails] = useState(false)
  const [types, setTypes] = useState([])
  const [venue, setVenue] = useState(null)
  const [venues, setVenues] = useState([])
  const [venueOptions, setVenueOptions] = useState([])
  const [hasSynchronizedStocks, setHasSynchronizedStocks] = useState(false)
  const [formFields, setFormFields] = useState(Object.keys(DEFAULT_FORM_VALUES))
  const [readOnlyFields, setReadOnlyFields] = useState([''])
  const [formErrors, setFormErrors] = useState(submitErrors)
  const [isBusy, setIsBusy] = useState(true)

  useEffect(() => {
    // retrieve data on mount

    pcapi.loadTypes().then(receivedTypes => setTypes(receivedTypes))
    pcapi
      .getValidatedOfferers()
      .then(offerers => buildSelectOptions('id', 'name', offerers))
      .then(offererOptions => setOffererOptions(offererOptions))
  }, [])

  useEffect(() => {
    setFormErrors(submitErrors)
  }, [submitErrors])

  useEffect(() => {
    // Initialize creation / edition form data

    let values = {}
    if (offer) {
      values = Object.keys(DEFAULT_FORM_VALUES).reduce((acc, field) => {
        if (field in offer) {
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
      setHasSynchronizedStocks(isSynchronized)
      if (isSynchronized) {
        setReadOnlyFields(Object.keys(DEFAULT_FORM_VALUES))
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
    } else {
      values = { ...DEFAULT_FORM_VALUES, ...initialValues }
    }

    setFormValues(values)
    setIsBusy(false)
  }, [initialValues, offer])

  useEffect(() => {
    // retrieve venues selected offerer

    let offererId = formValues.offererId
    if (offererId === DEFAULT_FORM_VALUES.offererId) {
      offererId = null
    }

    if (isUserAdmin && !offererId) {
      setVenues([])
    } else {
      pcapi.getVenuesForOfferer(offererId).then(receivedVenues => {
        setVenues(receivedVenues)
      })
    }
  }, [formValues.offererId, isUserAdmin])

  useEffect(() => {
    // filter venue options for selected type

    let venuesToShow = venues
    if (offerType?.offlineOnly) {
      venuesToShow = venuesToShow.filter(venue => !venue.isVirtual)
    } else if (offerType?.onlineOnly) {
      venuesToShow = venuesToShow.filter(venue => venue.isVirtual)
    }
    setVenueOptions(buildSelectOptions('id', 'name', venuesToShow))

    if (venuesToShow.length) {
      if (formValues.venueId && !venuesToShow.find(venue => venue.id === formValues.venueId)) {
        setFormValues({ ...formValues, venueId: DEFAULT_FORM_VALUES.venueId })
      }
      const venueFieldIdx = readOnlyFields.findIndex(fieldName => fieldName === 'venueId')
      if (venueFieldIdx !== -1) {
        readOnlyFields.splice(venueFieldIdx, 1)
        setReadOnlyFields(readOnlyFields)
      }
    } else if (!readOnlyFields.includes('venueId')) {
      setReadOnlyFields([...readOnlyFields, 'venueId'])
    }
  }, [formValues, offerType, readOnlyFields, venues])

  useEffect(() => {
    // store useful objects for selected venueId and type

    if (formValues.type) {
      setOfferType(types.find(type => type.value === formValues.type))
    }
    if (formValues.venueId) {
      setVenue(venues.find(venue => venue.id === formValues.venueId))
    }
  }, [formValues, types, venues])

  useEffect(() => {
    // build form fields

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

    setFormFields(newFormFields)
  }, [offerType, isUserAdmin, receiveNotificationEmails, venue])

  const isValid = useCallback(() => {
    const optionalFields = [
      'author',
      'bookingEmail',
      'isbn',
      'isDuo',
      'isNational',
      'musicType',
      'musicSubType',
      'performer',
      'showType',
      'showSubType',
      'stageDirector',
      'speaker',
      'url',
      'visa',
      'withdrawalDetails',
    ]

    let newFormErrors = {}
    formFields.forEach(fieldName => {
      if (optionalFields.includes(fieldName)) {
        return
      }

      if (formValues[fieldName] === DEFAULT_FORM_VALUES[fieldName]) {
        newFormErrors[fieldName] = 'Ce champs est obligatoire.'
      }
    })

    setFormErrors(newFormErrors)
    return Object.keys(newFormErrors).length === 0
  }, [formFields, formValues])

  useEffect(() => {
    if (onChange) {
      onChange(formValues)
    }
  }, [formValues, onChange])

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

      const submitedValues = formFields.reduce((acc, fieldName) => {
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

      onSubmit(submitedValues)
    } else {
      // TODO rlecellier: Add page notification "you've got some errors !"
      // use NotificationV2
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [formFields, formValues, isValid, onSubmit])

  const handleFormUpdate = useCallback(
    newFormValues => setFormValues(oldFormValues => ({ ...oldFormValues, ...newFormValues })),
    [setFormValues]
  )

  useEffect(() => {
    if (venue && venue.managingOffererId) {
      handleFormUpdate({ offererId: venue.managingOffererId })
    }
  }, [handleFormUpdate, venue])

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
        <h2 className="section-title">
          {"Type d'offre"}
        </h2>
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

        {hasSynchronizedStocks && (
          <div className="form-row">
            <SynchronizableProviderInformation offer={offer} />
          </div>
        )}
      </section>

      {displayFullForm && (
        <Fragment>
          <section className="form-section">
            <h2 className="section-title">
              {'Infos artistiques'}
            </h2>

            <div className="form-row">
              <TextInput
                error={getErrorMessage('name')}
                label="Titre de l'offre"
                name="name"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('name')}
                required
                type="text"
                value={formValues.name}
              />
            </div>
            <div className="form-row">
              <TextareaInput
                countCharacters
                error={getErrorMessage('description')}
                label="Description"
                maxLength={1000}
                name="description"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('description')}
                required
                rows={6}
                value={formValues.description}
              />
            </div>
            {formFields.includes('speaker') && (
              <TextInput
                error={getErrorMessage('speaker')}
                label="Intervenant"
                name="speaker"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('speaker')}
                type="text"
                value={formValues.speaker}
              />
            )}

            {formFields.includes('author') && (
              <TextInput
                error={getErrorMessage('author')}
                label="Auteur"
                name="author"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('author')}
                type="text"
                value={formValues.author}
              />
            )}

            {formFields.includes('visa') && (
              <TextInput
                error={getErrorMessage('visa')}
                label="Visa d’exploitation"
                name="visa"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('visa')}
                type="text"
                value={formValues.visa}
              />
            )}

            {formFields.includes('isbn') && (
              <TextInput
                error={getErrorMessage('isbn')}
                label="ISBN"
                name="isbn"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('isbn')}
                type="text"
                value={formValues.isbn}
              />
            )}

            {formFields.includes('stageDirector') && (
              <TextInput
                error={getErrorMessage('stageDirector')}
                label="Metteur en scène"
                name="stageDirector"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('stageDirector')}
                type="text"
                value={formValues.stageDirector}
              />
            )}

            {formFields.includes('performer') && (
              <TextInput
                error={getErrorMessage('perforer')}
                label="Interprète"
                name="performer"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('performer')}
                type="text"
                value={formValues.performer}
              />
            )}
          </section>

          <section className="form-section">
            <h2 className="section-title">
              {'Informations pratiques'}
            </h2>
            <p className="section-description">
              {
                'Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande.'
              }
            </p>

            <div className="form-row">
              <TextareaInput
                countCharacters
                error={getErrorMessage('withdrawalDetails')}
                label="Informations de retrait"
                maxLength={500}
                name="withdrawalDetails"
                onChange={handleSingleFormUpdate}
                readOnly={readOnlyFields.includes('withdrawalDetails')}
                required
                rows={4}
                sublabel="Optionnel"
                value={formValues.withdrawalDetails}
              />
            </div>

            {formFields.includes('url') && (
              <div className="form-row">
                <TextInput
                  error={getErrorMessage('url')}
                  label="URL"
                  name="url"
                  onChange={handleSingleFormUpdate}
                  readOnly={readOnlyFields.includes('url')}
                  required
                  sublabel={
                    !readOnlyFields.includes('url') &&
                    'Vous pouvez inclure {token} {email} et {offerId} dans l’URL, qui seront remplacés respectivement par le code de la contremarque, l’e-mail de la personne ayant reservé et l’identifiant de l’offre'
                  }
                  type="text"
                  value={formValues.url}
                />
              </div>
            )}

            {formFields.includes('durationMinutes') && (
              <div className="form-row">
                <TimeInput
                  error={getErrorMessage('durationMinutes')}
                  label="Durée"
                  name="durationMinutes"
                  onChange={handleDurationChange}
                  placeholder="HH:MM"
                  type="duration"
                  value={formValues.durationMinutes}
                />
              </div>
            )}

            <div className="form-row">
              <Select
                defaultOption={{
                  displayName: 'Sélectionnez une structure',
                  id: SELECT_DEFAULT_VALUE,
                }}
                error={getErrorMessage('offererId')}
                handleSelection={handleSingleFormUpdate}
                isDisabled={readOnlyFields.includes('offererId')}
                label="Structure"
                name="offererId"
                options={offererOptions}
                selectedValue={formValues.offererId}
              />
            </div>
            <div className="form-row">
              <Select
                defaultOption={{
                  displayName: 'Sélectionnez un lieu',
                  id: SELECT_DEFAULT_VALUE,
                }}
                error={getErrorMessage('venueId')}
                handleSelection={handleSingleFormUpdate}
                isDisabled={readOnlyFields.includes('venueId')}
                label="Lieu"
                name="venueId"
                options={venueOptions}
                selectedValue={formValues.venueId}
              />
            </div>
            {displayRefundWarning && (
              <div className="form-row">
                <OfferRefundWarning />
              </div>
            )}
          </section>

          {offer && (
            <section className="form-section">
              <h2 className="section-title">
                {'Gestion des stocks et des accroches'}
              </h2>
              <div className="form-row">
                <MediationsManager offer={offer} />
              </div>
            </section>
          )}

          <section className="form-section">
            <h2 className="section-title">
              {'Autre'}
            </h2>

            {formFields.includes('isNational') && (
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
            {formFields.includes('isDuo') && (
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

            {formFields.includes('bookingEmail') && (
              <div className="form-row">
                <TextInput
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
  onChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default OfferForm
