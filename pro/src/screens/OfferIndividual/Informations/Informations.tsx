import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  OfferIndividualForm,
  setDefaultInitialFormValues,
  setFormReadOnlyFields,
  setInitialFormValues,
  validationSchema,
} from 'components/OfferIndividualForm'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import {
  createIndividualOffer,
  getOfferIndividualAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { MailOutlineIcon } from 'icons'

import { ActionBar } from '../ActionBar'
import { useIndividualOfferImageUpload } from '../hooks'
import { logTo } from '../utils/logTo'

import { filterCategories } from './utils'
import { computeNextStep } from './utils/computeNextStep'
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
  const location = useLocation()
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

  const isWithdrawalUpdatedMailActive = useActiveFeature(
    'WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL'
  )

  const [isSubmittingDraft, setIsSubmittingDraft] = useState<boolean>(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const { search } = useLocation()
  const offerSubtype = getOfferSubtypeFromParamsOrOffer(search, offer)
  const categoryStatus = getCategoryStatusFromOfferSubtype(offerSubtype)
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
  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    categoryStatus,
    isOfferSubtypeEvent(offerSubtype)
  )

  const [isWithdrawalDialogOpen, setIsWithdrawalDialogOpen] =
    useState<boolean>(false)

  const [shouldSendMail, setShouldSendMail] = useState<boolean>(false)

  const widthdrawalHasChanged = () => {
    const withdrawalToCheck = [
      'withdrawalDetails',
      'withdrawalDelay',
      'withdrawalType',
    ]

    return withdrawalToCheck.some(value => {
      const valueMeta = formik.getFieldMeta(value)
      if (
        valueMeta &&
        valueMeta.touched &&
        valueMeta.value != valueMeta.initialValue
      ) {
        return true
      }
      return false
    })
  }

  const handleSendMail = async (sendMail: boolean) => {
    if (!offer?.isActive) {
      return
    }

    const totalBookingsQuantity = offer?.stocks.reduce(
      (acc, stock) => acc + stock.bookingsQuantity,
      0
    )

    const hasWithdrawalDialogAction =
      (!isWithdrawalDialogOpen && widthdrawalHasChanged()) ||
      isWithdrawalDialogOpen

    if (
      totalBookingsQuantity &&
      totalBookingsQuantity > 0 &&
      hasWithdrawalDialogAction
    ) {
      setIsWithdrawalDialogOpen(!isWithdrawalDialogOpen)
      setShouldSendMail(sendMail)
      return
    }
  }

  const handleNextStep =
    ({ saveDraft = false, sendMail = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)

      if (isWithdrawalUpdatedMailActive && mode === OFFER_WIZARD_MODE.EDITION) {
        await handleSendMail(sendMail)
      }

      setIsSubmittingDraft(saveDraft)
      if (Object.keys(formik.errors).length !== 0) {
        /* istanbul ignore next: DEBT, TO FIX */
        setIsClickingFromActionBar(false)
        /* istanbul ignore next: DEBT, TO FIX */
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
    if (isWithdrawalDialogOpen) {
      return
    }
    const { isOk, payload } = !offer
      ? await createIndividualOffer(formValues)
      : await updateIndividualOffer({
          serializedOffer: serializePatchOffer({
            offer,
            formValues,
            shouldSendMail,
          }),
          offerId: offer.nonHumanizedId,
        })

    const nextStep = computeNextStep(
      mode,
      isSubmittingDraft,
      Boolean(isOfferSubtypeEvent(offerSubtype))
    )
    if (isOk) {
      const receivedOfferId = payload.nonHumanizedId
      await handleImageOnSubmit(receivedOfferId)

      const response = await getOfferIndividualAdapter(receivedOfferId)
      // This do not trigger a visal change, it's complicated to test
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
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

      notify.success(
        mode === OFFER_WIZARD_MODE.EDITION
          ? 'Vos modifications ont bien été enregistrées'
          : 'Brouillon sauvegardé dans la liste des offres'
      )
    } else {
      formik.setErrors(payload.errors)
    }
    setIsClickingFromActionBar(false)
  }

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

  const handlePreviousStep = () => {
    if (!formik.dirty) {
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        to: OFFER_FORM_HOMEPAGE,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: offer?.nonHumanizedId,
      })
    }
    const queryParams = new URLSearchParams(location.search)
    const queryOffererId = queryParams.get('structure')
    const queryVenueId = queryParams.get('lieu')
    /* istanbul ignore next: DEBT, TO FIX */
    navigate({
      pathname: '/offre/creation',
      search:
        queryOffererId && queryVenueId
          ? `lieu=${queryVenueId}&structure=${queryOffererId}`
          : queryOffererId && !queryVenueId
          ? `structure=${queryOffererId}`
          : '',
    })
  }

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
            onClickPrevious={handlePreviousStep}
            onClickNext={handleNextStep()}
            onClickSaveDraft={handleNextStep({ saveDraft: true })}
            step={OFFER_WIZARD_STEP_IDS.INFORMATIONS}
            isDisabled={
              formik.isSubmitting ||
              Boolean(offer && isOfferDisabled(offer.status)) ||
              isWithdrawalDialogOpen
            }
            offerId={offer?.nonHumanizedId}
            shouldTrack={shouldTrack}
          />
        </form>
      </FormLayout>

      {isWithdrawalUpdatedMailActive && isWithdrawalDialogOpen && (
        <ConfirmDialog
          cancelText="Ne pas envoyer"
          confirmText="Envoyer un email"
          leftButtonAction={handleNextStep({ saveDraft: true })}
          onCancel={() => {
            setIsWithdrawalDialogOpen(false)
            setIsClickingFromActionBar(false)
          }}
          onConfirm={handleNextStep({
            saveDraft: true,
            sendMail: true,
          })}
          icon={MailOutlineIcon}
          title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
        />
      )}

      <RouteLeavingGuardOfferIndividual
        when={formik.dirty && !isClickingFromActionBar}
        tracking={nextLocation =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            to: logTo(nextLocation),
            used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
            isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
            isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
            // FIX ME: it is always undefined at first creation (not sure it is possible)
            offerId: offer?.nonHumanizedId,
          })
        }
      />
    </FormikProvider>
  )
}

export default Informations
