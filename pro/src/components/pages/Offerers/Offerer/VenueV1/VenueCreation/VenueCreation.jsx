import React, { useCallback, useEffect, useState } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit, parseSubmitErrors } from 'react-final-form-utils'
import { useHistory, useParams } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { unhumanizeSiret } from 'core/Venue/utils'
import ConfirmDialog from 'new_components/ConfirmDialog'
import GoBackLink from 'new_components/GoBackLink'
import {
  createVenue,
  getOfferer,
  getVenueLabels,
  getVenueTypes,
} from 'repository/pcapi/pcapi'
import { sortByLabel } from 'utils/strings'

import ReturnOrSubmitControl from '../controls/ReturnOrSubmitControl/ReturnOrSubmitControl'
import AccessibilityFields, {
  autoFillNoDisabilityCompliantDecorator,
} from '../fields/AccessibilityFields'
import BankInformation from '../fields/BankInformationFields'
import BusinessUnitFields from '../fields/BankInformationFields/BusinessUnitFields'
import ContactInfosFields from '../fields/ContactInfosFields'
import IdentifierFields, {
  bindGetSiretInformationToSiret,
} from '../fields/IdentifierFields'
import LocationFields, {
  FRANCE_POSITION,
  bindGetSuggestionsToLatitude,
  bindGetSuggestionsToLongitude,
} from '../fields/LocationFields'
import WithdrawalDetailsFields from '../fields/WithdrawalDetailsFields'
import NotificationMessage from '../Notification'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import VenueType from '../ValueObjects/VenueType'
import EACInformation from '../VenueEdition/EACInformation'

const VenueCreation = () => {
  const [isReady, setIsReady] = useState(false)
  const [offerer, setOfferer] = useState(null)
  const [venueTypes, setVenueTypes] = useState(null)
  const [venueLabels, setVenueLabels] = useState(null)
  const [isCancelDialogOpen, setIsCancelDialogOpen] = useState(false)
  const [isSiretValued, setIsSiretValued] = useState(true)
  const [canOffererCreateCollectiveOffer, setCanOffererCreateCollectiveOffer] =
    useState(false)

  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  const isEntrepriseApiDisabled = useActiveFeature('DISABLE_ENTERPRISE_API')
  const isNewBankInformationCreation = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )
  const enableAdageVenueInformation = useActiveFeature(
    'ENABLE_ADAGE_VENUE_INFORMATION'
  )
  const { offererId } = useParams()
  const history = useHistory()
  const notify = useNotification()
  const { currentUser } = useCurrentUser()

  const formInitialValues = {
    managingOffererId: offererId,
    bookingEmail: currentUser.email,
  }

  useEffect(() => {
    const handleInitialRequest = async () => {
      const offererRequest = getOfferer(offererId)
      const venueTypesRequest = getVenueTypes().then(venueTypes => {
        return venueTypes.map(type => new VenueType(type))
      })
      const venueLabelsRequest = getVenueLabels().then(labels =>
        sortByLabel(labels)
      )
      const canOffererCreateCollectiveOfferRequest = enableAdageVenueInformation
        ? canOffererCreateCollectiveOfferAdapter(offererId).then(
            ({ payload }) => payload.isOffererEligibleToEducationalOffer
          )
        : Promise.resolve(false)

      const [
        offerer,
        venueTypes,
        venueLabels,
        canOffererCreateCollectiveOffer,
      ] = await Promise.all([
        offererRequest,
        venueTypesRequest,
        venueLabelsRequest,
        canOffererCreateCollectiveOfferRequest,
      ])
      return {
        offerer,
        venueTypes,
        venueLabels,
        canOffererCreateCollectiveOffer,
      }
    }
    handleInitialRequest().then(
      ({
        offerer,
        venueTypes,
        venueLabels,
        canOffererCreateCollectiveOffer,
      }) => {
        setOfferer(offerer)
        setVenueTypes(venueTypes)
        setVenueLabels(venueLabels)
        setCanOffererCreateCollectiveOffer(canOffererCreateCollectiveOffer)
        setIsReady(true)
      }
    )
  }, [offererId])

  const handleSubmitRequest = async ({
    formValues,
    handleFail,
    handleSuccess,
  }) => {
    const body = formatVenuePayload(formValues, true, isSiretValued)
    try {
      const response = await createVenue(body)
      handleSuccess(response)
    } catch (responseError) {
      handleFail(responseError)
    }
  }
  const handleSubmitFailNotification = errors => {
    let text = 'Une ou plusieurs erreurs sont présentes dans le formulaire.'
    if (errors.global) {
      text = `${text} ${errors.global[0]}`
    }

    notify.error(text)
  }

  const handleSubmitSuccessNotification = payload => {
    const notificationMessageProps = {
      venueId: payload.id,
      offererId,
    }
    notify.success(<NotificationMessage {...notificationMessageProps} />)
  }

  const handleFormFail = formResolver => payload => {
    const errors = parseSubmitErrors(payload.errors)
    handleSubmitFailNotification(payload.errors)
    formResolver(errors)
  }

  const handleFormSuccess = formResolver => payload => {
    handleSubmitSuccessNotification(payload)
    formResolver()
    const next = isNewBankInformationCreation
      ? `/structures/${offererId}/lieux/${payload.id}?modification`
      : `/accueil?structure=${offererId}`
    history.push(next, isNewBankInformationCreation)
  }

  const handleOnFormSubmit = formValues => {
    return new Promise(formResolver => {
      handleSubmitRequest({
        formValues,
        handleFail: handleFormFail(formResolver),
        handleSuccess: handleFormSuccess(formResolver),
      })
    })
  }
  const openCancelDialog = useCallback(() => {
    setIsCancelDialogOpen(true)
  }, [])

  const closeCancelDialog = useCallback(() => {
    setIsCancelDialogOpen(false)
  }, [])
  const handleCancelConfirm = () => {
    history.replace(`/accueil?structure=${offererId}`)
  }

  const onHandleRender = formProps => {
    const readOnly = false
    const canSubmit = getCanSubmit(formProps)
    const { form, handleSubmit, values } = formProps
    const {
      isLocationFrozen: formIsLocationFrozen,
      latitude: formLatitude,
      longitude: formLongitude,
      siret: formSiret,
    } = values

    const siretValidOnCreation =
      !!formSiret && unhumanizeSiret(formSiret).length === 14 && isSiretValued
    return (
      <form name="venue" onSubmit={handleSubmit}>
        <IdentifierFields
          fieldReadOnlyBecauseFrozenFormSiret={siretValidOnCreation}
          formSiret={formSiret}
          isCreatedEntity
          readOnly={readOnly}
          siren={offerer.siren}
          updateIsSiretValued={setIsSiretValued}
          venueLabels={venueLabels}
          venueTypes={venueTypes}
        />
        <LocationFields
          fieldReadOnlyBecauseFrozenFormSiret={siretValidOnCreation}
          form={form}
          formIsLocationFrozen={formIsLocationFrozen}
          formLatitude={
            formLatitude === '' ? FRANCE_POSITION.latitude : formLatitude
          }
          formLongitude={
            formLongitude === '' ? FRANCE_POSITION.longitude : formLongitude
          }
          readOnly={readOnly}
          isAddressRequired={true}
        />
        <AccessibilityFields />
        <WithdrawalDetailsFields isCreatedEntity readOnly={readOnly} />
        <ContactInfosFields readOnly={false} />
        {enableAdageVenueInformation && canOffererCreateCollectiveOffer && (
          <EACInformation venue={null} offererId={offererId} isCreatingVenue />
        )}
        {!isNewBankInformationCreation &&
          (isBankInformationWithSiretActive ? (
            <BusinessUnitFields isCreatingVenue offerer={offerer} />
          ) : (
            <BankInformation offerer={offerer} />
          ))}
        <hr />
        <div
          className="field is-grouped is-grouped-centered"
          style={{ justifyContent: 'space-between' }}
        >
          <button
            className="secondary-button"
            onClick={openCancelDialog}
            type="reset"
          >
            Quitter
          </button>

          <ReturnOrSubmitControl
            canSubmit={canSubmit}
            isCreatedEntity
            isNewBankInformationCreation={isNewBankInformationCreation}
            isRequestPending={formProps.submitting}
            offererId={offererId}
            readOnly={readOnly}
          />
        </div>
      </form>
    )
  }

  const decorators = [
    autoFillNoDisabilityCompliantDecorator,
    bindGetSuggestionsToLatitude,
    bindGetSuggestionsToLongitude,
  ]
  if (!isEntrepriseApiDisabled) {
    decorators.push(bindGetSiretInformationToSiret)
  }

  return (
    <div className="venue-page">
      <GoBackLink to={`/accueil?structure=${offererId}`} title="Accueil" />
      <PageTitle title="Créer un lieu" />
      <Titles title="Lieu" />
      <p className="advice">Ajoutez un lieu où accéder à vos offres.</p>

      {!isReady && <Spinner />}
      {isCancelDialogOpen && (
        <ConfirmDialog
          cancelText="Annuler"
          confirmText="Quitter sans enregistrer"
          onCancel={closeCancelDialog}
          onConfirm={handleCancelConfirm}
          title="Voulez-vous quitter la création de lieu ?"
        >
          <p>
            Votre lieu ne sera pas sauvegardé et toutes les informations seront
            perdues.
          </p>
        </ConfirmDialog>
      )}

      {isReady && (
        <Form
          decorators={decorators}
          name="venue"
          initialValues={formInitialValues}
          onSubmit={handleOnFormSubmit}
          render={onHandleRender}
        />
      )}
    </div>
  )
}
export default VenueCreation
