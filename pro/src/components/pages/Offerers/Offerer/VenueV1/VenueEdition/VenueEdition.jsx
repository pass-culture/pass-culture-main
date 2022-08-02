import React, { useCallback, useEffect, useRef, useState } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { useDispatch } from 'react-redux'
import { Link, useHistory, useLocation, useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import useNotification from 'components/hooks/useNotification'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import GoBackLink from 'new_components/GoBackLink'
import * as pcapi from 'repository/pcapi/pcapi'
import { showNotification } from 'store/reducers/notificationReducer'
import { Banner } from 'ui-kit'
import { sortByLabel } from 'utils/strings'

import ModifyOrCancelControl from '../controls/ModifyOrCancelControl/ModifyOrCancelControl'
import ReturnOrSubmitControl from '../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'
import AccessibilityFields, {
  autoFillNoDisabilityCompliantDecorator,
} from '../fields/AccessibilityFields'
import BankInformation from '../fields/BankInformationFields/BankInformationFields'
import BusinessUnitFields from '../fields/BankInformationFields/BusinessUnitFields'
import ContactInfosFields from '../fields/ContactInfosFields'
import IdentifierFields from '../fields/IdentifierFields/IdentifierFields'
import bindGetSuggestionsToLatitude from '../fields/LocationFields/decorators/bindGetSuggestionsToLatitude'
import bindGetSuggestionsToLongitude from '../fields/LocationFields/decorators/bindGetSuggestionsToLongitude'
import LocationFields from '../fields/LocationFields/LocationFields'
import { FRANCE_POSITION } from '../fields/LocationFields/utils/positions'
import ReimbursementFields from '../fields/ReimbursementFields/ReimbursementFields'
import WithdrawalDetailsFields from '../fields/WithdrawalDetailsFields/WithdrawalDetailsFields'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import VenueType from '../ValueObjects/VenueType'

import DeleteBusinessUnitConfirmationDialog from './DeleteBusinessUnitConfirmationDialog/DeleteBusinessUnitConfirmationDialog'
import { DisplayVenueInAppLink } from './DisplayVenueInAppLink'
import EACInformation from './EACInformation'
import { ImageVenueUploaderSection } from './ImageVenueUploaderSection/ImageVenueUploaderSection'
import VenueProvidersManager from './VenueProvidersManager'
import VenueProvidersManagerV2 from './VenueProvidersManagerV2'

const VenueEdition = () => {
  const [isRequestPending, setIsRequestPending] = useState(false)
  const [showConfirmationDialog, setShowConfirmationDialog] = useState(false)
  const [isReady, setIsReady] = useState(false)
  const [offerer, setOfferer] = useState(null)
  const [venue, setVenue] = useState(null)
  const [venueTypes, setVenueTypes] = useState(null)
  const [venueLabels, setVenueLabels] = useState(null)
  const [canOffererCreateCollectiveOffer, setCanOffererCreateCollectiveOffer] =
    useState(false)

  const deleteBusinessUnitConfirmed = useRef(false)
  const { offererId, venueId } = useParams()
  const history = useHistory()
  const dispatch = useDispatch()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  const isNewBankInformationCreation = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )
  const enableAdageVenueInformation = useActiveFeature(
    'ENABLE_ADAGE_VENUE_INFORMATION'
  )
  const isEnabledNewVenueProviderSection = useActiveFeature(
    'ENABLE_PRO_NEW_VENUE_PROVIDER_UI'
  )

  const onImageUpload = useCallback(
    ({ bannerUrl, bannerMeta }) => {
      setVenue({
        ...venue,
        bannerUrl,
        bannerMeta,
      })
    },
    [venue]
  )

  const handleSubmitRequest = async ({
    formValues,
    handleFail,
    handleSuccess,
  }) => {
    const body = formatVenuePayload(formValues, false, venue.siret !== null)
    try {
      const response = await pcapi.editVenue(venueId, body)
      handleSuccess(response)
    } catch (responseError) {
      handleFail(responseError)
    }
  }

  const handleSubmitRequestFail = ({ payload: { errors } }) => {
    let text = 'Une ou plusieurs erreurs sont présentes dans le formulaire.'
    if (errors.global) {
      text = `${text} ${errors.global[0]}`
    }

    dispatch(
      showNotification({
        text,
        type: 'error',
      })
    )
  }

  const handleSubmitRequestSuccess = (_action, { hasDelayedUpdates }) => {
    const text = hasDelayedUpdates
      ? 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes'
      : 'Vos modifications ont bien été prises en compte'
    dispatch(
      showNotification({
        text,
        type: hasDelayedUpdates ? 'pending' : 'success',
      })
    )
  }

  const onDeleteImage = useCallback(() => {
    setVenue({
      ...venue,
      bannerUrl: undefined,
      bannerMeta: undefined,
    })
  }, [venue])

  const shouldDisplayImageVenueUploaderSection = venue?.isPermanent

  useEffect(() => {
    const handleInitialRequest = async () => {
      const offererRequest = pcapi.getOfferer(offererId)
      const venueRequest = api.getVenue(venueId)
      const venueTypesRequest = pcapi.getVenueTypes().then(venueTypes => {
        return venueTypes.map(type => new VenueType(type))
      })
      const venueLabelsRequest = pcapi
        .getVenueLabels()
        .then(labels => sortByLabel(labels))
      const canOffererCreateCollectiveOfferRequest = enableAdageVenueInformation
        ? canOffererCreateCollectiveOfferAdapter(offererId)
        : Promise.resolve({
            payload: { isOffererEligibleToEducationalOffer: false },
            isOk: true,
            message: null,
          })

      const [
        offerer,
        venue,
        venueTypes,
        venueLabels,
        canOffererCreateCollectiveOfferResponse,
      ] = await Promise.all([
        offererRequest,
        venueRequest,
        venueTypesRequest,
        venueLabelsRequest,
        canOffererCreateCollectiveOfferRequest,
      ])

      return {
        offerer,
        venue,
        venueTypes,
        venueLabels,
        canOffererCreateCollectiveOffer:
          canOffererCreateCollectiveOfferResponse.payload
            .isOffererEligibleToEducationalOffer,
      }
    }
    handleInitialRequest().then(
      ({
        offerer,
        venue,
        venueTypes,
        venueLabels,
        canOffererCreateCollectiveOffer,
      }) => {
        setOfferer(offerer)
        setVenue(venue)
        setVenueTypes(venueTypes)
        setVenueLabels(venueLabels)
        setIsReady(true)
        setCanOffererCreateCollectiveOffer(canOffererCreateCollectiveOffer)
      }
    )
  }, [offererId, venueId])

  useEffect(() => {
    if (venue?.initialIsVirtual && !isBankInformationWithSiretActive) {
      history.push('/404')
      return null
    }
  }, [venue?.initialIsVirtual, history, isBankInformationWithSiretActive])

  useEffect(() => {
    if (history.location.state) {
      const { collectiveDataEditionSuccess, scrollToElementId, ...state } =
        history.location.state

      if (collectiveDataEditionSuccess) {
        notify.success(collectiveDataEditionSuccess)
      }

      if (scrollToElementId) {
        // wait for react to mount component

        const element = document.getElementById(scrollToElementId)
        element?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
          inline: 'center',
        })
      }

      // remove state to avoid notification in case of page reload
      history.replace(history.location, { ...state, scrollToElementId })
    }
  }, [
    history.location.state,
    // element depends on these 2 variables otherwise it is not in the DOM so we need them in the dependency array
    enableAdageVenueInformation,
    canOffererCreateCollectiveOffer,
  ])

  const onConfirmDeleteBusinessUnit = submit => {
    deleteBusinessUnitConfirmed.current = true
    setShowConfirmationDialog(false)
    submit()
  }

  const handleFormFail = formResolver => (_state, action) => {
    const { payload } = action
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitRequestFail(action)
    formResolver(errors)
    setIsRequestPending(false)
  }

  const handleFormSuccess =
    (formResolver, hasDelayedUpdates) => (_state, action) => {
      const queryParams = new URLSearchParams(location.search)
      queryParams.delete('modification')
      handleSubmitRequestSuccess(action, { hasDelayedUpdates })
      formResolver()
      history.replace(`${location.pathname}?${queryParams.toString()}`)
      setIsRequestPending(false)
    }

  const handleOnFormSubmit = formValues => {
    if (
      !deleteBusinessUnitConfirmed.current &&
      venue.isBusinessUnitMainVenue &&
      formValues.businessUnitId != venue.businessUnitId
    ) {
      setShowConfirmationDialog(true)
      return
    }
    deleteBusinessUnitConfirmed.current = false
    setIsRequestPending(true)
    const hasDelayedUpdates = [
      formValues.isAccessibilityAppliedOnAllOffers,
      formValues.isWithdrawalAppliedOnAllOffers,
      formValues.isEmailAppliedOnAllOffers,
    ].includes(true)

    return new Promise(resolve => {
      handleSubmitRequest({
        formValues,
        handleFail: handleFormFail(resolve),
        handleSuccess: handleFormSuccess(resolve, hasDelayedUpdates),
      })
    })
  }

  const onHandleRender = formProps => {
    const queryParams = new URLSearchParams(location.search)
    const readOnly = queryParams.get('modification') === null

    const {
      siret: initialSiret,
      isVirtual: initialIsVirtual,
      withdrawalDetails: initialWithdrawalDetails,
    } = venue || {}
    const canSubmit = getCanSubmit({
      isLoading: formProps.isLoading,
      dirtySinceLastSubmit: formProps.dirtySinceLastSubmit,
      hasSubmitErrors: formProps.hasSubmitErrors,
      hasValidationErrors: formProps.hasValidationErrors,
      pristine: formProps.pristine,
    })
    const { form, handleSubmit, values } = formProps

    const {
      bookingEmail,
      isLocationFrozen: formIsLocationFrozen,
      latitude: formLatitude,
      longitude: formLongitude,
      siret: formSiret,
      venueTypeCode,
      venueLabelId,
    } = values

    const cancelBusinessUnitModification = form => {
      form.change('businessUnitId', venue.businessUnitId)
      setShowConfirmationDialog(false)
    }

    const isDirtyFieldBookingEmail = bookingEmail !== venue.bookingEmail

    const siretValidOnModification = initialSiret !== null
    const fieldReadOnlyBecauseFrozenFormSiret =
      !readOnly && siretValidOnModification

    return (
      <>
        <form
          data-testid="venue-edition-form"
          name="venue"
          onSubmit={handleSubmit}
        >
          <IdentifierFields
            fieldReadOnlyBecauseFrozenFormSiret={
              fieldReadOnlyBecauseFrozenFormSiret
            }
            formSiret={formSiret}
            initialSiret={initialSiret}
            isDirtyFieldBookingEmail={isDirtyFieldBookingEmail}
            isToggleDisabled
            readOnly={readOnly || initialIsVirtual}
            venueIsVirtual={initialIsVirtual}
            venueLabelId={venueLabelId}
            venueLabels={venueLabels}
            venueTypeCode={venueTypeCode}
            venueTypes={venueTypes}
          />
          {!!shouldDisplayImageVenueUploaderSection && (
            <ImageVenueUploaderSection
              onDeleteImage={onDeleteImage}
              onImageUpload={onImageUpload}
              venueBanner={venue.bannerMeta}
              venueId={venue.id}
              venueImage={venue.bannerUrl}
            />
          )}
          {!initialIsVirtual && (
            <>
              <LocationFields
                fieldReadOnlyBecauseFrozenFormSiret={
                  fieldReadOnlyBecauseFrozenFormSiret
                }
                form={form}
                formIsLocationFrozen={formIsLocationFrozen}
                formLatitude={
                  formLatitude === '' ? FRANCE_POSITION.latitude : formLatitude
                }
                formLongitude={
                  formLongitude === ''
                    ? FRANCE_POSITION.longitude
                    : formLongitude
                }
                readOnly={readOnly}
                isAddressRequired={false}
              />
              <AccessibilityFields
                formValues={values}
                readOnly={readOnly}
                venue={venue}
              />
              <WithdrawalDetailsFields
                initialWithdrawalDetails={initialWithdrawalDetails}
                readOnly={readOnly}
              />
              <ContactInfosFields readOnly={readOnly} />
            </>
          )}
          {enableAdageVenueInformation && canOffererCreateCollectiveOffer && (
            <EACInformation venue={venue} offererId={offererId} />
          )}
          {isNewBankInformationCreation ? (
            <ReimbursementFields
              offerer={offerer}
              readOnly={readOnly}
              scrollToSection={location.state}
              venue={venue}
            />
          ) : isBankInformationWithSiretActive ? (
            // FIXME
            // the first response on offerers do not return  venue.BusinessUnit
            // the second on venues does
            venue.businessUnit !== undefined && (
              <BusinessUnitFields
                offerer={offerer}
                readOnly={readOnly}
                scrollToSection={location.state}
                venue={venue}
              />
            )
          ) : (
            <BankInformation offerer={offerer} venue={venue} />
          )}
          <hr />
          <div
            className="field is-grouped is-grouped-centered"
            style={{ justifyContent: 'space-between' }}
          >
            <ModifyOrCancelControl
              form={form}
              history={history}
              offererId={offererId}
              readOnly={readOnly}
              venueId={venueId}
            />
            <ReturnOrSubmitControl
              canSubmit={canSubmit}
              isRequestPending={isRequestPending}
              offererId={offererId}
              readOnly={readOnly}
            />
          </div>
        </form>
        {showConfirmationDialog && (
          <DeleteBusinessUnitConfirmationDialog
            onCancel={() => cancelBusinessUnitModification(form)}
            onConfirm={() => onConfirmDeleteBusinessUnit(handleSubmit)}
          />
        )}
      </>
    )
  }

  const getVirtualVenueName = () => `${offerer.name} (Offre numérique)`

  const getInitialValues = venue => {
    let initialValues = { ...venue, venueSiret: venue.pricingPoint?.id }
    const accessibilityFieldNames = [
      'audioDisabilityCompliant',
      'mentalDisabilityCompliant',
      'motorDisabilityCompliant',
      'visualDisabilityCompliant',
    ]
    accessibilityFieldNames.forEach(fieldName => {
      if (initialValues[fieldName] === null) {
        delete initialValues[fieldName]
      }
    })

    if (initialValues.isVirtual) {
      initialValues.name = getVirtualVenueName()
    }

    return initialValues
  }

  const renderForm = () => {
    const initialValues = getInitialValues(venue)
    const decorators = [
      autoFillNoDisabilityCompliantDecorator,
      bindGetSuggestionsToLatitude,
      bindGetSuggestionsToLongitude,
    ]

    return (
      <Form
        decorators={decorators}
        initialValues={initialValues}
        name="venue"
        onSubmit={handleOnFormSubmit}
        render={formProps => {
          return onHandleRender(formProps)
        }}
      />
    )
  }
  const queryParams = new URLSearchParams(location.search)
  const readOnly = queryParams.get('modification') === null

  const {
    id: initialId,
    isVirtual: initialIsVirtual,
    name: initialName,
  } = venue || {}

  const pageTitle = readOnly ? 'Détails de votre lieu' : 'Modifier votre lieu'

  const actionLink = !!initialId && (
    <Link
      className="primary-button with-icon"
      onClick={() =>
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_FORM_NAVIGATION_IN.VENUE,
          to: OFFER_FORM_HOMEPAGE,
          used: OFFER_FORM_NAVIGATION_MEDIUM.VENUE_BUTTON,
          isEdition: false,
        })
      }
      to={`/offre/creation?lieu=${initialId}&structure=${offererId}`}
    >
      <AddOfferSvg />
      <span>Créer une offre</span>
    </Link>
  )

  const pageSubtitle = initialIsVirtual ? getVirtualVenueName() : initialName

  if (!venue) return null

  return (
    <div className="venue-page">
      <div className="venue-page-links">
        <GoBackLink to={`/accueil?structure=${offererId}`} title="Accueil" />
        {venue.isPermanent && (
          <DisplayVenueInAppLink nonHumanizedId={venue.nonHumanizedId} />
        )}
      </div>
      {!isNewBankInformationCreation &&
        venue.businessUnit &&
        !venue.businessUnit.siret && (
          <Banner
            className="banner-invalid-bu"
            href={`/structures/${offererId}/point-de-remboursement/`}
            icon="ico-right-circle-arrow"
            linkTitle="Rattacher votre lieu à un point de remboursement valide"
          >
            Ce lieu n’est pas rattaché à un point de remboursement valide. Pour
            continuer à percevoir vos remboursements, veuillez renseigner un
            SIRET de référence pour votre point de remboursement.
          </Banner>
        )}
      <PageTitle title={pageTitle} />
      <Titles
        action={actionLink || undefined}
        subtitle={pageSubtitle}
        description={
          venue && venue.dmsToken && isNewBankInformationCreation
            ? `N° d'identifiant du lieu : ${venue.dmsToken}`
            : ''
        }
        title="Lieu"
      />
      {venue &&
        !initialIsVirtual &&
        (isEnabledNewVenueProviderSection ? (
          <VenueProvidersManagerV2 venue={venue} />
        ) : (
          <VenueProvidersManager venue={venue} />
        ))}
      {venue && offerer && isReady && renderForm()}
    </div>
  )
}

export default VenueEdition
