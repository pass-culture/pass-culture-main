import AccessibilityCheckboxList, {
  getAccessibilityValues,
} from './AccessibilityCheckboxList'
import {
  BASE_OFFER_FIELDS,
  CAN_CREATE_FROM_ISBN_SUBCATEGORIES,
  DEFAULT_FORM_VALUES,
  EXTRA_DATA_FIELDS,
  MANDATORY_FIELDS,
  NOT_REIMBURSED,
  PLATFORM,
  TEXT_INPUT_DEFAULT_VALUE,
  WITHDRAWAL_BY_EMAIL_DELAY_OPTIONS,
  WITHDRAWAL_ON_SITE_DELAY_OPTIONS,
  WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE,
} from '../_constants'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import React, {
  Fragment,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react'

import CheckboxInput from 'components/layout/inputs/CheckboxInput'
import DurationInput from 'components/layout/inputs/DurationInput/DurationInput'
import InternalBanner from 'components/layout/InternalBanner'
import { Link } from 'react-router-dom'
import { OFFER_WITHDRAWAL_TYPE_OPTIONS } from 'core/Offers'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferCategories from './OfferCategories'
import OfferOptions from './OfferOptions'
import { OfferRefundWarning } from 'new_components/Banner'
import { OfferWithdrawalTypeOptions } from './OfferWithdrawalTypeOptions'
import PropTypes from 'prop-types'
import Select from 'components/layout/inputs/Select'
import Spinner from 'components/layout/Spinner'
import { SubmitButton } from 'ui-kit'
import SynchronizedProviderInformation from './SynchronisedProviderInfos'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import TextareaInput from 'components/layout/inputs/TextareaInput'
import WithdrawalReminder from './Messages/WithdrawalReminder'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'
import isEqual from 'lodash.isequal'
import { isUrlValid } from './validators'
import { sortByDisplayName } from 'utils/strings'
import useActiveFeature from 'components/hooks/useActiveFeature'
import { useSelector } from 'react-redux'

// JOCONDE React:component "Ce composant est vraiment le plus beau et le plus lisible que nous ayons côté pro. Prenez en de la graine !"

const OfferForm = ({
  areAllVenuesVirtual,
  backUrl,
  categories,
  initialValues,
  isDisabled,
  isEdition,
  isUserAdmin,
  offerersNames,
  onSubmit,
  providerName,
  readOnlyFields,
  setSelectedOfferer,
  setOfferPreviewData,
  showErrorNotification,
  subCategories,
  submitErrors,
  userEmail,
  venues,
}) => {
  const [offerSubCategory, setOfferSubCategory] = useState(null)
  const [receiveNotificationEmails, setReceiveNotificationEmails] =
    useState(false)
  const [venue, setVenue] = useState(null)
  const [formValues, setFormValues] = useState({})
  const [venueOptions, setVenueOptions] = useState(
    sortByDisplayName(
      venues.map(item => ({
        id: item['id'].toString(),
        displayName: item['publicName'] ? item['publicName'] : item['name'],
      }))
    )
  )
  const [offerFormFields, setOfferFormFields] = useState(
    Object.keys(DEFAULT_FORM_VALUES)
  )
  const [formErrors, setFormErrors] = useState(submitErrors)
  const formRef = useRef(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitLoading, setIsSubmitLoading] = useState(false)
  const logEvent = useSelector(state => state.app.logEvent)

  const isIsbnRequiredInLivreEditionEnabled = useActiveFeature(
    'ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION'
  )

  const [mandatoryFields, setMandatoryFields] = useState([...MANDATORY_FIELDS])

  const resetMandatoryFields = useCallback(() => {
    if (
      MANDATORY_FIELDS.sort().join(' ') !== mandatoryFields.sort().join(' ')
    ) {
      setMandatoryFields([...MANDATORY_FIELDS])
    }
  }, [mandatoryFields])

  const handleFormUpdate = useCallback(
    newFormValues =>
      setFormValues(oldFormValues => {
        const updatedFormValues = { ...oldFormValues, ...newFormValues }
        if (
          oldFormValues['subcategoryId'] !== updatedFormValues['subcategoryId']
        ) {
          updatedFormValues['withdrawalType'] =
            DEFAULT_FORM_VALUES['withdrawalType']
          updatedFormValues['withdrawalDelay'] =
            DEFAULT_FORM_VALUES['withdrawalDelay']
        }

        return isEqual(oldFormValues, updatedFormValues)
          ? oldFormValues
          : updatedFormValues
      }),
    [setFormValues]
  )

  const offererOptions = sortByDisplayName(
    offerersNames.map(item => ({
      id: item['id'].toString(),
      displayName: item['name'],
    }))
  )

  const setOfferVenue = useCallback(
    newVenueId => {
      if (readOnlyFields.includes('venueId')) {
        return
      }

      let updatedValues = {
        venueId: newVenueId,
      }
      const venue = venues.find(venue => venue.id === updatedValues.venueId)
      if (venue) {
        const venueAccessibilities = {
          audioDisabilityCompliant: venue.audioDisabilityCompliant,
          mentalDisabilityCompliant: venue.mentalDisabilityCompliant,
          motorDisabilityCompliant: venue.motorDisabilityCompliant,
          visualDisabilityCompliant: venue.visualDisabilityCompliant,
        }
        const haveUnsetAccessibility =
          Object.values(venueAccessibilities).includes(null)
        updatedValues = {
          ...updatedValues,
          ...Object.keys(venueAccessibilities).reduce(
            (acc, field) => ({
              ...acc,
              [field]: !!venueAccessibilities[field],
            }),
            {}
          ),
          noDisabilityCompliant: haveUnsetAccessibility
            ? false
            : !Object.values(venueAccessibilities).includes(true),
        }
      }
      handleFormUpdate(updatedValues)
    },
    [handleFormUpdate, readOnlyFields, venues]
  )

  useEffect(() => {
    resetMandatoryFields()
    if (
      isIsbnRequiredInLivreEditionEnabled &&
      CAN_CREATE_FROM_ISBN_SUBCATEGORIES.includes(offerSubCategory?.id)
    ) {
      mandatoryFields.push('isbn')
    }
    if (offerSubCategory?.conditionalFields.includes('musicType')) {
      mandatoryFields.push('musicType')
    }
    if (offerSubCategory?.conditionalFields.includes('showType')) {
      mandatoryFields.push('showType')
    }
    if (
      WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(offerSubCategory?.id)
    ) {
      mandatoryFields.push('withdrawalType')

      if (
        formValues.withdrawalType === OFFER_WITHDRAWAL_TYPE_OPTIONS.ON_SITE ||
        formValues.withdrawalType === OFFER_WITHDRAWAL_TYPE_OPTIONS.BY_EMAIL
      ) {
        mandatoryFields.push('withdrawalDelay')
      }
    }
  }, [
    formValues,
    offerSubCategory,
    isIsbnRequiredInLivreEditionEnabled,
    mandatoryFields,
    resetMandatoryFields,
  ])

  useEffect(() => {
    setFormErrors(submitErrors)
  }, [submitErrors])

  useEffect(
    function initializeFormData() {
      // If formValues have been initiliazed we've nothing to do.
      if (Object.keys(formValues).length > 0) {
        return
      }

      if (
        initialValues.bookingEmail &&
        initialValues.bookingEmail !== DEFAULT_FORM_VALUES.bookingEmail
      ) {
        setReceiveNotificationEmails(true)
      }

      setFormValues({ ...DEFAULT_FORM_VALUES, ...initialValues })
      const accessibilityInitialValues = getAccessibilityValues(initialValues)
      if (
        'venueId' in initialValues &&
        Object.values(accessibilityInitialValues).includes(null)
      ) {
        setOfferVenue(initialValues.venueId)
      }
      setIsLoading(false)
    },
    [formValues, initialValues, setFormValues, setOfferVenue]
  )

  useEffect(
    function buildFormFields() {
      const isVenueVirtual = venue?.isVirtual
      const offerConditionalFields = getOfferConditionalFields({
        offerSubCategory,
        isUserAdmin,
        receiveNotificationEmails,
        isVenueVirtual,
      })
      let offerSubCategoryConditionalFields = offerSubCategory
        ? offerSubCategory.conditionalFields
        : []

      const newFormFields = [
        ...BASE_OFFER_FIELDS,
        ...offerSubCategoryConditionalFields,
        ...offerConditionalFields,
      ]
      setOfferFormFields(newFormFields)
    },
    [
      formValues,
      offerSubCategory,
      isUserAdmin,
      receiveNotificationEmails,
      venue,
    ]
  )

  useEffect(
    function filterVenueOptionsForSelectedType() {
      let venuesToShow = venues

      if (offerSubCategory?.onlineOfflinePlatform === PLATFORM.ONLINE) {
        venuesToShow = venuesToShow.filter(venue => venue.isVirtual)
      } else if (offerSubCategory?.onlineOfflinePlatform === PLATFORM.OFFLINE) {
        venuesToShow = venuesToShow.filter(venue => !venue.isVirtual)
      }

      setVenueOptions(
        sortByDisplayName(
          venuesToShow.map(item => ({
            id: item['id'].toString(),
            displayName: item['publicName'] ? item['publicName'] : item['name'],
          }))
        )
      )

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
        setOfferVenue(venuesToShow[0].id)
      }
    },
    [offerSubCategory, setOfferVenue, venues]
  )

  useEffect(
    function storeOfferSubCategoryAndVenueWhenSelected() {
      if (formValues.subcategoryId) {
        setOfferSubCategory(
          subCategories.find(type => type.id === formValues.subcategoryId)
        )
      }

      if (
        formValues.venueId &&
        venueOptions.find(showedVenue => showedVenue.id === formValues.venueId)
      ) {
        const selectedVenue = venues.find(
          venue => venue.id === formValues.venueId
        )
        if (selectedVenue) {
          setVenue(selectedVenue)
          handleFormUpdate({ offererId: selectedVenue.managingOffererId })
        }
      } else {
        setVenue(null)
      }
    },
    [
      formValues.subcategoryId,
      formValues.venueId,
      handleFormUpdate,
      venues,
      venueOptions,
      subCategories,
    ]
  )

  useEffect(
    function selectOffererWhenUnique() {
      if (offerersNames.length === 1) {
        handleFormUpdate({ offererId: offerersNames[0].id })
      }
    },
    [handleFormUpdate, offerersNames]
  )

  useEffect(
    function setBookingEmail() {
      if (!initialValues.bookingEmail) {
        if (
          (offerSubCategory &&
            offerSubCategory.onlineOfflinePlatform === PLATFORM.ONLINE) ||
          venue?.isVirtual
        ) {
          handleFormUpdate({ bookingEmail: userEmail })
        } else if (venue) {
          handleFormUpdate({ bookingEmail: venue.bookingEmail })
        }
      }
    },
    [
      initialValues.bookingEmail,
      venue,
      offerSubCategory,
      handleFormUpdate,
      userEmail,
    ]
  )

  useEffect(
    function setVenueValues() {
      if (venue === null) return

      if (
        venue.withdrawalDetails &&
        formValues.withdrawalDetails ===
          DEFAULT_FORM_VALUES['withdrawalDetails']
      ) {
        handleFormUpdate({ withdrawalDetails: venue.withdrawalDetails })
      }
    },
    [formValues.withdrawalDetails, venue, handleFormUpdate]
  )

  useEffect(() => {
    if (formRef.current) {
      const invalidElement = formRef.current.querySelector('.error')

      if (invalidElement && invalidElement.value === '') {
        const scrollBehavior = doesUserPreferReducedMotion() ? 'auto' : 'smooth'

        invalidElement.scrollIntoView({
          behavior: scrollBehavior,
          block: 'center',
          inline: 'center',
        })
      }
    }
  }, [formRef, formErrors])

  useEffect(
    function setParentOfferPreviewData() {
      setOfferPreviewData({
        subcategoryId: formValues.subcategoryId,
        description: formValues.description,
        isEvent: offerSubCategory?.isEvent || false,
        isDuo: formValues.isDuo,
        name: formValues.name,
        venueId: formValues.venueId,
        withdrawalDetails: formValues.withdrawalDetails,
      })
    },
    [
      formValues.subcategoryId,
      formValues.description,
      formValues.isDuo,
      formValues.name,
      formValues.venueId,
      formValues.withdrawalDetails,
      offerSubCategory,
      setOfferPreviewData,
    ]
  )

  const selectOfferer = useCallback(
    event => {
      const selectedOffererId = event.target.value
      if (selectedOffererId !== formValues.offererId) {
        handleFormUpdate({
          offererId: selectedOffererId,
          venueId: DEFAULT_FORM_VALUES.venueId,
        })
        setSelectedOfferer(selectedOffererId)
      }
    },
    [formValues.offererId, handleFormUpdate, setSelectedOfferer]
  )

  const isValid = useCallback(() => {
    let newFormErrors = {}
    const formFields = [...offerFormFields, 'offererId']

    mandatoryFields.forEach(fieldName => {
      if (
        formFields.includes(fieldName) &&
        formValues[fieldName] === DEFAULT_FORM_VALUES[fieldName]
      ) {
        newFormErrors[fieldName] = 'Ce champ est obligatoire.'
      }
    })

    if (
      ![
        formValues.noDisabilityCompliant,
        formValues.audioDisabilityCompliant,
        formValues.mentalDisabilityCompliant,
        formValues.motorDisabilityCompliant,
        formValues.visualDisabilityCompliant,
      ].includes(true)
    ) {
      newFormErrors['disabilityCompliant'] = 'Ce champ est obligatoire.'
    }

    if (!isUrlValid(formValues.url)) {
      newFormErrors['url'] = 'Veuillez renseigner une URL valide'
    }

    if (!isUrlValid(formValues.externalTicketOfficeUrl)) {
      newFormErrors['externalTicketOfficeUrl'] =
        'Veuillez renseigner une URL valide'
    }

    if (
      WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(
        formValues.subcategoryId
      ) &&
      !formValues.withdrawalType
    ) {
      newFormErrors[
        'withdrawalType'
      ] = `Vous devez cocher l'une des options ci-dessus`
    }

    setFormErrors(newFormErrors)
    return Object.keys(newFormErrors).length === 0
  }, [offerFormFields, mandatoryFields, formValues])

  const submitForm = useCallback(
    async event => {
      event.preventDefault()
      setIsSubmitLoading(true)

      if (isValid()) {
        const editableFields = offerFormFields.filter(
          field => !readOnlyFields.includes(field)
        )

        const submittedValuesAccumulator = editableFields.some(editableField =>
          EXTRA_DATA_FIELDS.includes(editableField)
        )
          ? { extraData: null }
          : {}

        const submittedValues = editableFields.reduce(
          (submittedValues, fieldName) => {
            if (!EXTRA_DATA_FIELDS.includes(fieldName)) {
              const fieldValue =
                formValues[fieldName] === TEXT_INPUT_DEFAULT_VALUE
                  ? null
                  : formValues[fieldName]
              submittedValues = {
                ...submittedValues,
                [fieldName]: fieldValue,
              }
            } else if (
              formValues[fieldName] !== DEFAULT_FORM_VALUES[fieldName]
            ) {
              submittedValues.extraData = {
                ...submittedValues.extraData,
                [fieldName]: formValues[fieldName],
              }
            }

            return submittedValues
          },
          submittedValuesAccumulator
        )

        // front should check categoryId but do not send to backend
        delete submittedValues.categoryId

        if (!receiveNotificationEmails) {
          submittedValues.bookingEmail = null
        }

        if (
          submittedValues.withdrawalType &&
          submittedValues.withdrawalType ===
            OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET
        ) {
          submittedValues.withdrawalDelay = null
        }

        const nextStepRedirect = await onSubmit(submittedValues)
        if (nextStepRedirect !== null) {
          logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OfferBreadcrumbStep.DETAILS,
            to: OfferBreadcrumbStep.STOCKS,
            used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
          })
          await nextStepRedirect()
          return
        }
      } else {
        showErrorNotification()
      }
      setIsSubmitLoading(false)
    },
    [
      offerFormFields,
      formValues,
      isValid,
      onSubmit,
      readOnlyFields,
      receiveNotificationEmails,
      showErrorNotification,
    ]
  )

  const onCancelClick = () => {
    if (isEdition)
      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OfferBreadcrumbStep.DETAILS,
        to: OfferBreadcrumbStep.SUMMARY,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      })
  }

  const handleChangeVenue = useCallback(
    event => {
      setOfferVenue(event.target.value)
    },
    [setOfferVenue]
  )

  const resetFormError = useCallback(
    field => {
      if (field in formErrors) {
        let newFormErrors = { ...formErrors }
        delete newFormErrors[field]
        setFormErrors(newFormErrors)
      }
    },
    [formErrors, setFormErrors]
  )

  const handleSingleFormUpdate = event => {
    const field = event.target.name

    const value =
      event.target.type === 'checkbox' ? !formValues[field] : event.target.value
    if (value !== null) {
      resetFormError(field)
    }
    handleFormUpdate({ [field]: value })
  }

  const updateWithdrawalType = event => {
    handleSingleFormUpdate(event)

    resetFormError('withdrawalDelay')
    handleFormUpdate({
      withdrawalDelay:
        event.target.value === OFFER_WITHDRAWAL_TYPE_OPTIONS.ON_SITE ||
        event.target.value === OFFER_WITHDRAWAL_TYPE_OPTIONS.BY_EMAIL
          ? WITHDRAWAL_ON_SITE_DELAY_OPTIONS[0].id
          : DEFAULT_FORM_VALUES['withdrawalDelay'],
    })
  }

  const handleDisabilityCompliantUpdate = useCallback(
    disabilityCompliantValues => {
      if (Object.values(disabilityCompliantValues).includes(true)) {
        resetFormError('disabilityCompliant')
      }

      handleFormUpdate(disabilityCompliantValues)
    },
    [handleFormUpdate, resetFormError]
  )

  const handleDurationChange = value =>
    handleFormUpdate({ durationMinutes: value })

  const toggleReceiveNotification = useCallback(
    () => setReceiveNotificationEmails(!receiveNotificationEmails),
    [setReceiveNotificationEmails, receiveNotificationEmails]
  )

  const displayNoRefundWarning =
    offerSubCategory && offerSubCategory.reimbursementRule === NOT_REIMBURSED

  const getErrorMessage = fieldName => {
    return fieldName in formErrors ? formErrors[fieldName] : null
  }

  const getIsbnErrorMessage = () => {
    const isbnErrorMessage = getErrorMessage('isbn')

    if (
      isIsbnRequiredInLivreEditionEnabled &&
      isbnErrorMessage &&
      isbnErrorMessage.includes(
        'Ce produit n’est pas éligible au pass Culture.'
      )
    ) {
      return (
        <>
          {isbnErrorMessage}
          <b>
            {
              ' Vous pouvez retrouver la liste des catégories de livres qui ne sont pas éligibles au pass Culture sur le lien suivant:'
            }
            <a
              href="https://aide.passculture.app/fr/articles/5394354-acteurs-culturels-quels-sont-les-livres-eligibles-au-pass-culture"
              rel="noopener noreferrer"
              target="_blank"
              title="Consulter le FAQ"
            >
              {' FAQ'}
            </a>
          </b>
        </>
      )
    }
    return isbnErrorMessage
  }

  const isTypeOfflineButOnlyVirtualVenues =
    offerSubCategory &&
    offerSubCategory.onlineOfflinePlatform === PLATFORM.OFFLINE &&
    areAllVenuesVirtual

  // If one of disability fields is disabled, all of them are.
  const isDisabilityFieldsReadOnly =
    readOnlyFields.filter(field =>
      [
        'audioDisabilityCompliant',
        'mentalDisabilityCompliant',
        'motorDisabilityCompliant',
        'visualDisabilityCompliant',
      ].includes(field)
    ).length > 0

  if (isLoading) {
    return <Spinner />
  }

  return (
    <form className="offer-form" ref={formRef}>
      {providerName !== null ? (
        <SynchronizedProviderInformation providerName={providerName} />
      ) : (
        <p className="page-subtitle">
          Tous les champs sont obligatoires sauf mention contraire.
        </p>
      )}

      <section className="form-section">
        <h3 className="section-title">Type d’offre</h3>
        <p className="section-description">
          Le type de l’offre permet de la caractériser et de la valoriser au
          mieux dans l’application.
        </p>

        <div className="form-row">
          <OfferCategories
            categories={categories}
            categoriesFormValues={{
              categoryId: formValues.categoryId,
              subcategoryId: formValues.subcategoryId,
              musicType: formValues.musicType,
              musicSubType: formValues.musicSubType,
              showType: formValues.showType,
              showSubType: formValues.showSubType,
            }}
            getErrorMessage={getErrorMessage}
            isTypeOfflineButOnlyVirtualVenues={
              isTypeOfflineButOnlyVirtualVenues
            }
            isVirtualOffer={initialValues.isVirtualVenue}
            readOnlyFields={readOnlyFields}
            resetFormError={resetFormError}
            subCategories={subCategories}
            updateCategoriesFormValues={handleFormUpdate}
            updateFormErrors={setFormErrors}
          />
          {isTypeOfflineButOnlyVirtualVenues && (
            <InternalBanner
              extraClassName="no-physical-venue"
              href={`/structures/${formValues.offererId}/lieux/creation`}
              linkTitle="+ Ajouter un lieu"
              subtitle="Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures."
              type="notification-info"
            />
          )}
        </div>
      </section>

      {formValues.subcategoryId !== DEFAULT_FORM_VALUES.subcategoryId &&
        !isTypeOfflineButOnlyVirtualVenues && (
          <Fragment>
            <section className="form-section">
              <h3 className="section-title">Informations artistiques</h3>

              <div className="form-row">
                <TextInput
                  countCharacters
                  disabled={readOnlyFields.includes('name')}
                  error={getErrorMessage('name')}
                  label="Titre de l'offre"
                  maxLength={90}
                  name="name"
                  onChange={handleSingleFormUpdate}
                  required
                  subLabel={
                    !mandatoryFields.includes('name') ? 'Optionnel' : ''
                  }
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
                  subLabel={
                    !mandatoryFields.includes('description') ? 'Optionnel' : ''
                  }
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
                    subLabel={
                      !mandatoryFields.includes('speaker') ? 'Optionnel' : ''
                    }
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
                    subLabel={
                      !mandatoryFields.includes('author') ? 'Optionnel' : ''
                    }
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
                    subLabel={
                      !mandatoryFields.includes('visa') ? 'Optionnel' : ''
                    }
                    type="text"
                    value={formValues.visa}
                  />
                </div>
              )}

              {offerFormFields.includes('isbn') && (
                <div className="form-row">
                  <TextInput
                    disabled={readOnlyFields.includes('isbn')}
                    error={getIsbnErrorMessage()}
                    label="ISBN"
                    name="isbn"
                    onChange={handleSingleFormUpdate}
                    required={isIsbnRequiredInLivreEditionEnabled}
                    subLabel={
                      !mandatoryFields.includes('isbn') ? 'Optionnel' : ''
                    }
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
                    subLabel={
                      !mandatoryFields.includes('stageDirector')
                        ? 'Optionnel'
                        : ''
                    }
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
                    subLabel={
                      !mandatoryFields.includes('performer') ? 'Optionnel' : ''
                    }
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
                    subLabel={
                      !mandatoryFields.includes('durationMinutes')
                        ? 'Optionnel'
                        : ''
                    }
                  />
                </div>
              )}
            </section>

            <section className="form-section">
              <h3 className="section-title">Informations pratiques</h3>
              <p className="section-description">
                Les informations pratiques permettent de donner aux utilisateurs
                des informations sur le retrait de leur commande.
              </p>

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
                  selectedValue={
                    formValues.offererId || DEFAULT_FORM_VALUES.offererId
                  }
                  subLabel={
                    !mandatoryFields.includes('offererId') ? 'Optionnel' : ''
                  }
                />
              </div>

              <div className="form-row">
                <Select
                  defaultOption={{
                    displayName: 'Sélectionnez un lieu',
                    id: DEFAULT_FORM_VALUES.venueId,
                  }}
                  error={getErrorMessage('venueId')}
                  handleSelection={handleChangeVenue}
                  isDisabled={
                    readOnlyFields.includes('venueId') || venue?.isVirtual
                  }
                  label="Lieu"
                  name="venueId"
                  options={venueOptions}
                  selectedValue={
                    formValues.venueId || DEFAULT_FORM_VALUES.venueId
                  }
                  subLabel={
                    !mandatoryFields.includes('venueId') ? 'Optionnel' : ''
                  }
                />
              </div>
              {displayNoRefundWarning && (
                <div className="form-row">
                  <OfferRefundWarning />
                </div>
              )}

              {!offerSubCategory?.isEvent && venue && !venue.isVirtual && (
                <div className="form-row">
                  <WithdrawalReminder />
                </div>
              )}

              {WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(
                formValues.subcategoryId
              ) && (
                <>
                  <OfferWithdrawalTypeOptions
                    error={getErrorMessage('withdrawalType')}
                    updateWithdrawalType={updateWithdrawalType}
                    withdrawalType={formValues.withdrawalType}
                  />
                  {formValues.withdrawalType ===
                    OFFER_WITHDRAWAL_TYPE_OPTIONS.ON_SITE && (
                    <div className="form-row">
                      <Select
                        error={getErrorMessage('withdrawalDelay')}
                        handleSelection={handleSingleFormUpdate}
                        label="Heure de retrait"
                        name="withdrawalDelay"
                        options={WITHDRAWAL_ON_SITE_DELAY_OPTIONS}
                        rightLabel="avant le début de l’évènement"
                        selectedValue={formValues.withdrawalDelay}
                      />
                    </div>
                  )}
                  {formValues.withdrawalType ===
                    OFFER_WITHDRAWAL_TYPE_OPTIONS.BY_EMAIL && (
                    <div className="form-row">
                      <Select
                        error={getErrorMessage('withdrawalDelay')}
                        handleSelection={handleSingleFormUpdate}
                        label="Date d'envoi"
                        name="withdrawalDelay"
                        options={WITHDRAWAL_BY_EMAIL_DELAY_OPTIONS}
                        rightLabel="avant le début de l’évènement"
                        selectedValue={formValues.withdrawalDelay}
                      />
                    </div>
                  )}
                </>
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
                  subLabel={
                    !mandatoryFields.includes('withdrawalDetails')
                      ? 'Optionnel'
                      : ''
                  }
                  value={formValues.withdrawalDetails}
                />
              </div>

              {offerFormFields.includes('url') && (
                <div className="form-row">
                  <TextInput
                    disabled={readOnlyFields.includes('url')}
                    error={getErrorMessage('url')}
                    label="URL d’accès à l’offre"
                    longDescription="Vous pouvez inclure {token} {email} et {offerId} dans l’URL, qui seront remplacés respectivement par le code de la contremarque, l’e-mail de la personne ayant reservé et l’identifiant de l’offre"
                    name="url"
                    onChange={handleSingleFormUpdate}
                    required
                    type="text"
                    value={formValues.url}
                  />
                </div>
              )}

              {offerFormFields.includes('isNational') && (
                <div className="form-row">
                  <CheckboxInput
                    checked={formValues.isNational || false}
                    disabled={
                      readOnlyFields.includes('isNational') ? 'disabled' : ''
                    }
                    isLabelDisable={isDisabled}
                    label="Rayonnement national"
                    name="isNational"
                    onChange={handleSingleFormUpdate}
                  />
                </div>
              )}
            </section>

            <section className="form-section accessibility-section">
              <h3 className="section-title">Accessibilité</h3>
              <p className="section-description">
                Cette offre est-elle accessible aux publics en situation de
                handicaps :
              </p>
              <AccessibilityCheckboxList
                disabled={isDisabled}
                formValues={formValues}
                isInError={Boolean(getErrorMessage('disabilityCompliant'))}
                onChange={handleDisabilityCompliantUpdate}
                readOnly={isDisabilityFieldsReadOnly}
              />
            </section>

            <OfferOptions
              canOfferBeDuo={offerFormFields.includes('isDuo')}
              isDuo={formValues.isDuo}
              isDuoDisabled={readOnlyFields.includes('isDuo')}
              updateForm={handleFormUpdate}
            />

            <section className="form-section">
              <h3 className="section-title">Lien de réservation externe</h3>
              <p className="section-description">
                {'Ce lien sera affiché aux utilisateurs ne pouvant pas effectuer la réservation dans l’application. ' +
                  'Nous vous recommandons d’insérer le lien vers votre billetterie ou votre site internet.'}
              </p>
              <TextInput
                disabled={readOnlyFields.includes('externalTicketOfficeUrl')}
                error={getErrorMessage('externalTicketOfficeUrl')}
                label="URL de redirection externe"
                name="externalTicketOfficeUrl"
                onChange={handleSingleFormUpdate}
                subLabel={
                  !mandatoryFields.includes('externalTicketOfficeUrl')
                    ? 'Optionnel'
                    : ''
                }
                type="text"
                value={formValues.externalTicketOfficeUrl}
              />
            </section>

            <section className="form-section">
              <h3 className="section-title">Notifications</h3>

              <div className="form-row">
                <CheckboxInput
                  checked={receiveNotificationEmails}
                  disabled={readOnlyFields.includes('bookingEmail')}
                  isLabelDisable={isDisabled}
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
        <Link className="secondary-link" to={backUrl} onClick={onCancelClick}>
          {'Annuler et quitter'}
        </Link>
        <SubmitButton
          className="primary-button"
          disabled={isDisabled}
          isLoading={isSubmitLoading}
          onClick={submitForm}
        >
          {isEdition ? 'Enregistrer les modifications' : 'Étape suivante'}
        </SubmitButton>
      </section>
    </form>
  )
}

OfferForm.defaultProps = {
  areAllVenuesVirtual: false,
  backUrl: '',
  initialValues: {},
  isDisabled: false,
  isEdition: false,
  isUserAdmin: false,
  providerName: null,
  readOnlyFields: [],
  setSelectedOfferer: () => {},
}

OfferForm.propTypes = {
  areAllVenuesVirtual: PropTypes.bool,
  backUrl: PropTypes.string,
  categories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  initialValues: PropTypes.shape(),
  isDisabled: PropTypes.bool,
  isEdition: PropTypes.bool,
  isUserAdmin: PropTypes.bool,
  offerersNames: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
    })
  ).isRequired,
  onSubmit: PropTypes.func.isRequired,
  providerName: PropTypes.string,
  readOnlyFields: PropTypes.arrayOf(PropTypes.string),
  setOfferPreviewData: PropTypes.func.isRequired,
  setSelectedOfferer: PropTypes.func,
  showErrorNotification: PropTypes.func.isRequired,
  subCategories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  submitErrors: PropTypes.shape().isRequired,
  userEmail: PropTypes.string.isRequired,
  venues: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default OfferForm
