import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import {
  IndividualOfferFormValues,
  IndividualOfferForm,
  setDefaultInitialFormValues,
  setFormReadOnlyFields,
  setInitialFormValues,
  validationSchema,
} from 'components/IndividualOfferForm'
import {
  getFilteredVenueListByCategoryStatus,
  getFilteredVenueListBySubcategory,
} from 'components/IndividualOfferForm/utils/getFilteredVenueList'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import {
  createIndividualOffer,
  getIndividualOfferAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import strokeMailIcon from 'icons/stroke-mail.svg'

import { ActionBar } from '../ActionBar'
import { useIndividualOfferImageUpload } from '../hooks'
import { logTo } from '../utils/logTo'

import { filterCategories } from './utils'
import { computeNextStep } from './utils/computeNextStep'
import {
  getCategoryStatusFromOfferSubtype,
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from './utils/filterCategories/filterCategories'

export interface InformationsProps {
  offererId: string
  venueId: string
}

const Informations = ({
  offererId,
  venueId,
}: InformationsProps): JSX.Element => {
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
  } = useIndividualOfferContext()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useIndividualOfferImageUpload()

  const isBookingContactEnabled = useActiveFeature(
    'WIP_MANDATORY_BOOKING_CONTACT'
  )

  const [isSubmittingDraft, setIsSubmittingDraft] = useState<boolean>(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)

  const queryParams = new URLSearchParams(location.search)
  const querySubcategoryId = queryParams.get('sous-categorie')
  const queryOfferType = queryParams.get('offer-type')
  const querySubcategory = subCategories.find(
    subcategory => subcategory.id === querySubcategoryId
  )

  // querySubcategoryId & queryOfferType are mutually exclusive
  // but since it's on url, the user still could enter both
  // if it happens, we don't filter subcategories
  // so the user can always choose among all subcategories
  const offerSubtype = getOfferSubtypeFromParam(
    querySubcategoryId ? null : queryOfferType
  )
  const categoryStatus = getCategoryStatusFromOfferSubtype(offerSubtype)
  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    categoryStatus,
    isOfferSubtypeEvent(offerSubtype)
  )

  const filteredVenueList = querySubcategory
    ? getFilteredVenueListBySubcategory(venueList, querySubcategory)
    : getFilteredVenueListByCategoryStatus(venueList, categoryStatus)

  // offer is null when we are creating a new offer
  const initialValues: IndividualOfferFormValues =
    offer === null
      ? setDefaultInitialFormValues(
          offererNames,
          offererId,
          venueId,
          filteredVenueList,
          isBookingContactEnabled,
          querySubcategory
        )
      : setInitialFormValues(offer, subCategories, isBookingContactEnabled)

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
        valueMeta.value !== valueMeta.initialValue
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

      if (mode === OFFER_WIZARD_MODE.EDITION) {
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
    formValues: IndividualOfferFormValues
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
          offerId: offer.id,
        })

    const nextStep = computeNextStep(
      mode,
      isSubmittingDraft,
      Boolean(
        subCategories.find(
          subcategory => subcategory.id === formik.values.subcategoryId
        )?.isEvent
      )
    )
    if (isOk) {
      const receivedOfferId = payload.id
      await handleImageOnSubmit(receivedOfferId)

      const response = await getIndividualOfferAdapter(receivedOfferId)
      // This do not trigger a visal change, it's complicated to test
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      // replace url to fix back button
      navigate(
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          offerId: receivedOfferId,
          mode,
        }),
        { replace: true }
      )

      navigate(
        getIndividualOfferUrl({
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
        subcategoryId: formik.values.subcategoryId,
      })

      if (isSubmittingDraft) {
        notify.success('Brouillon sauvegardé dans la liste des offres')
      } else if (mode === OFFER_WIZARD_MODE.EDITION) {
        notify.success('Vos modifications ont bien été enregistrées')
      }
    } else {
      formik.setErrors(payload.errors)
      // This is used from scroll to error
      formik.setStatus('apiError')
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
        offerId: offer?.id,
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
          <IndividualOfferForm
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
            offerId={offer?.id}
            shouldTrack={shouldTrack}
          />
        </form>
      </FormLayout>
      {isWithdrawalDialogOpen && (
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
          icon={strokeMailIcon}
          title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
        />
      )}
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !isClickingFromActionBar}
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
        isEdition={mode === OFFER_WIZARD_MODE.EDITION}
      />
    </FormikProvider>
  )
}

export default Informations
