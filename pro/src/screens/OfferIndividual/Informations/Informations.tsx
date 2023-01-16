import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  OfferIndividualForm,
  setDefaultInitialFormValues,
  setFormReadOnlyFields,
  setInitialFormValues,
  validationSchema,
} from 'components/OfferIndividualForm'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers'
import {
  createIndividualOffer,
  getOfferIndividualAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'

import { ActionBar } from '../ActionBar'
import { useIndividualOfferImageUpload } from '../hooks'
import { logTo } from '../utils/logTo'

import { filterCategories } from './utils'
import {
  getCategoryStatusFromOfferSubtype,
  getOfferSubtypeFromParamsOrOffer,
  isOfferSubtypeEvent,
} from './utils/filterCategories/filterCategories'

export interface IInformationsProps {
  offererId: string
  venueId: string
}

const Informations = ({
  offererId,
  venueId,
}: IInformationsProps): JSX.Element => {
  const notify = useNotification()
  const { currentUser } = useCurrentUser()
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()
  const {
    offer,
    categories,
    subCategories,
    offererNames,
    venueList,
    setOffer,
    shouldTrack,
    setShouldTrack,
  } = useOfferIndividualContext()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useIndividualOfferImageUpload()

  const [isSubmittingDraft, setIsSubmittingDraft] = useState<boolean>(false)
  const [
    isSubmittingFromRouteLeavingGuard,
    setIsSubmittingFromRouteLeavingGuard,
  ] = useState<boolean>(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)
      setIsSubmittingDraft(saveDraft)
      if (Object.keys(formik.errors).length !== 0) {
        /* istanbul ignore next: DEBT, TO FIX */
        setIsClickingFromActionBar(false)
        if (saveDraft) {
          notify.error(
            'Des informations sont nécessaires pour sauvegarder le brouillon'
          )
        } else {
          notify.error(FORM_ERROR_MESSAGE)
        }
      }
      if (saveDraft) {
        await formik.submitForm()
      }
    }

  const onSubmitOffer = async (
    formValues: IOfferIndividualFormValues
  ): Promise<void> => {
    const { isOk, payload } = !offer
      ? await createIndividualOffer(formValues)
      : await updateIndividualOffer({ offer, formValues })

    const nextStep =
      mode === OFFER_WIZARD_MODE.EDITION
        ? OFFER_WIZARD_STEP_IDS.SUMMARY
        : isSubmittingDraft
        ? OFFER_WIZARD_STEP_IDS.INFORMATIONS
        : OFFER_WIZARD_STEP_IDS.STOCKS

    if (isOk) {
      const receivedOfferId = payload.id
      await handleImageOnSubmit(receivedOfferId)

      const response = await getOfferIndividualAdapter(payload.id)
      // This do not trigger a visal change, it's complicated to test
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      notify.success(
        mode === OFFER_WIZARD_MODE.EDITION
          ? 'Vos modifications ont bien été enregistrées'
          : 'Brouillon sauvegardé dans la liste des offres'
      )
      if (!isSubmittingFromRouteLeavingGuard) {
        // replace url to fix back button
        navigate(
          getOfferIndividualUrl({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            offerId: receivedOfferId,
            mode,
          }),
          { replace: true }
        )

        navigate(
          getOfferIndividualUrl({
            offerId: receivedOfferId,
            step: nextStep,
            mode,
          })
        )
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          to: nextStep,
          used: isSubmittingDraft
            ? OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS
            : OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
          isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
          isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
          offerId: receivedOfferId,
        })
      }
    } else {
      formik.setErrors(payload.errors)
    }
    setIsClickingFromActionBar(false)
  }

  const initialValues: IOfferIndividualFormValues =
    offer === null
      ? setDefaultInitialFormValues(
          FORM_DEFAULT_VALUES,
          offererNames,
          offererId,
          venueId,
          venueList
        )
      : setInitialFormValues(offer, subCategories)
  const readOnlyFields = setFormReadOnlyFields(offer, currentUser.isAdmin)

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOffer,
    validationSchema,
    // enableReinitialize is needed to reset dirty after submit (and not block after saving a draft)
    enableReinitialize: true,
  })

  useEffect(() => {
    // when form is dirty it's tracked by RouteLeavingGuard
    setShouldTrack(!formik.dirty)
  }, [formik.dirty])

  const initialVenue: TOfferIndividualVenue | undefined = venueList.find(
    venue => venue.id === initialValues.venueId
  )

  const { search } = useLocation()
  const offerSubtype = getOfferSubtypeFromParamsOrOffer(search, offer)
  const categoryStatus = getCategoryStatusFromOfferSubtype(offerSubtype)
  // TODO to remove once the hub that always redirects to the good url with query params is in prod
  const legacyCategoryStatus =
    initialVenue === undefined
      ? CATEGORY_STATUS.ONLINE_OR_OFFLINE
      : initialVenue.isVirtual
      ? CATEGORY_STATUS.ONLINE
      : CATEGORY_STATUS.OFFLINE
  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    offerSubtype !== null ? categoryStatus : legacyCategoryStatus,
    isOfferSubtypeEvent(offerSubtype)
  )

  return (
    <FormikProvider value={formik}>
      <FormLayout small>
        <form onSubmit={formik.handleSubmit}>
          <OfferIndividualForm
            offererNames={offererNames}
            venueList={venueList}
            categories={filteredCategories}
            subCategories={filteredSubCategories}
            readOnlyFields={readOnlyFields}
            onImageUpload={onImageUpload}
            onImageDelete={onImageDelete}
            imageOffer={imageOffer}
            offerSubtype={offerSubtype}
          />
          <ActionBar
            onClickNext={handleNextStep()}
            onClickSaveDraft={handleNextStep({ saveDraft: true })}
            step={OFFER_WIZARD_STEP_IDS.INFORMATIONS}
            isDisabled={formik.isSubmitting}
            offerId={offer?.id}
            shouldTrack={shouldTrack}
          />
        </form>
      </FormLayout>
      <RouteLeavingGuardOfferIndividual
        when={formik.dirty && !isClickingFromActionBar}
        saveForm={formik.submitForm}
        setIsSubmittingFromRouteLeavingGuard={
          setIsSubmittingFromRouteLeavingGuard
        }
        mode={mode}
        isFormValid={formik.isValid}
        tracking={nextLocation =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            to: logTo(nextLocation),
            used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
            isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
            isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
            // FIX ME: it is always undefined at first creation (not sure it is possible)
            offerId: offer?.id,
          })
        }
        hasOfferBeenCreated={!!offer?.id}
      />
    </FormikProvider>
  )
}

export default Informations
