import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import { CheckboxInput } from 'components/layout/inputs/CheckboxInput/CheckboxInput'
import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import TextareaInput from 'components/layout/inputs/TextareaInput'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import TimeInput from 'components/layout/inputs/TimeInput'
import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'

import { isAllocineOffer, isSynchronizedOffer } from '../../domain/localProvider'
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

const mandatoryFields = ['name', 'venueId', 'offererId', 'url']

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
  const { initialValues, isUserAdmin, offer, onSubmit, onChange, submitErrors } = props

  const [formValues, setFormValues] = useState({})
  const [offererOptions, setOffererOptions] = useState([])
  const [offerType, setOfferType] = useState(null)
  const [receiveNotificationEmails, setReceiveNotificationEmails] = useState(false)
  const [types, setTypes] = useState([])
  const [venue, setVenue] = useState(null)
  const [venues, setVenues] = useState([])
  const [venueOptions, setVenueOptions] = useState([])
  const [hasSynchronizedStocks, setHasSynchronizedStocks] = useState(false)
  const [offerFormFields, setOfferFormFields] = useState(Object.keys(DEFAULT_FORM_VALUES))
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
      if (!hasSynchronizedStocks && venueFieldIdx !== -1) {
        readOnlyFields.splice(venueFieldIdx, 1)
        setReadOnlyFields(readOnlyFields)
      }
    } else if (!readOnlyFields.includes('venueId')) {
      setReadOnlyFields([...readOnlyFields, 'venueId'])
    }
  }, [formValues, hasSynchronizedStocks, offerType, readOnlyFields, venues])

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

    setOfferFormFields(newFormFields)
  }, [offerType, isUserAdmin, receiveNotificationEmails, venue])

  const isValid = useCallback(() => {
    let newFormErrors = {}
    const formFields = [...offerFormFields, 'offererId']
    mandatoryFields.forEach(fieldName => {
      if (
        formFields.includes(fieldName) &&
        formValues[fieldName] === DEFAULT_FORM_VALUES[fieldName]
      ) {
        newFormErrors[fieldName] = 'Ce champs est obligatoire.'
      }
    })

    setFormErrors(newFormErrors)
    return Object.keys(newFormErrors).length === 0
  }, [offerFormFields, formValues])

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

      onSubmit(submitedValues)
    } else {
      // TODO rlecellier: Add page notification "you've got some errors !"
      // use NotificationV2
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [offerFormFields, formValues, isValid, onSubmit])

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
                disabled={readOnlyFields.includes('name')}
                error={getErrorMessage('name')}
                label="Titre de l'offre"
                name="name"
                onChange={handleSingleFormUpdate}
                required
                sublabel={!mandatoryFields.includes('name') ? 'Optionnel' : ''}
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
                sublabel={!mandatoryFields.includes('description') ? 'Optionnel' : ''}
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
                  sublabel={!mandatoryFields.includes('speaker') ? 'Optionnel' : ''}
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
                  sublabel={!mandatoryFields.includes('author') ? 'Optionnel' : ''}
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
                  sublabel={!mandatoryFields.includes('visa') ? 'Optionnel' : ''}
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
                  sublabel={!mandatoryFields.includes('isbn') ? 'Optionnel' : ''}
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
                  sublabel={!mandatoryFields.includes('stageDirector') ? 'Optionnel' : ''}
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
                  sublabel={!mandatoryFields.includes('performer') ? 'Optionnel' : ''}
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
                  sublabel={!mandatoryFields.includes('duration') ? 'Optionnel' : ''}
                  type="duration"
                  value={formValues.durationMinutes}
                />
              </div>
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
                sublabel={!mandatoryFields.includes('offererId') ? 'Optionnel' : ''}
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
                sublabel={!mandatoryFields.includes('venueId') ? 'Optionnel' : ''}
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
                sublabel={!mandatoryFields.includes('withdrawalDetails') ? 'Optionnel' : ''}
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
                  sublabel={
                    !readOnlyFields.includes('url') &&
                    'Vous pouvez inclure {token} {email} et {offerId} dans l’URL, qui seront remplacés respectivement par le code de la contremarque, l’e-mail de la personne ayant reservé et l’identifiant de l’offre'
                  }
                  type="text"
                  value={formValues.url}
                />
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
  onChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default OfferForm
