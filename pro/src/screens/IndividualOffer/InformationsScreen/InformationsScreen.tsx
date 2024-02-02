import { FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import FormLayout from 'components/FormLayout'
import {
  IndividualOfferFormValues,
  IndividualOfferForm,
  setDefaultInitialFormValues,
  setFormReadOnlyFields,
  setInitialFormValues,
  getValidationSchema,
} from 'components/IndividualOfferForm'
import {
  getFilteredVenueListByCategoryStatus,
  getFilteredVenueListBySubcategory,
} from 'components/IndividualOfferForm/utils/getFilteredVenueList'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import {
  createIndividualOffer,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import strokeMailIcon from 'icons/stroke-mail.svg'

import ActionBar from '../ActionBar/ActionBar'
import { useIndividualOfferImageUpload } from '../hooks/useIndividualOfferImageUpload'

import {
  filterCategories,
  getCategoryStatusFromOfferSubtype,
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from './utils/filterCategories/filterCategories'

export interface InformationsScreenProps {
  offererId: string
  venueId: string
}

const InformationsScreen = ({
  offererId,
  venueId,
}: InformationsScreenProps): JSX.Element => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { offer, categories, subCategories, offererNames, venueList } =
    useIndividualOfferContext()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useIndividualOfferImageUpload()

  const [isEvent, setIsEvent] = useState<boolean | undefined>(false)

  const isBookingContactEnabled = useActiveFeature(
    'WIP_MANDATORY_BOOKING_CONTACT'
  )

  const queryParams = new URLSearchParams(location.search)
  const querySubcategoryId = queryParams.get('sous-categorie')
  const queryOfferType = queryParams.get('offer-type')
  const querySubcategory = subCategories.find(
    (subcategory) => subcategory.id === querySubcategoryId
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
    ? getFilteredVenueListBySubcategory(venueList, querySubcategory).filter(
        (venue) => venue.managingOffererId === Number(offererId)
      )
    : getFilteredVenueListByCategoryStatus(venueList, categoryStatus).filter(
        (venue) => venue.managingOffererId === Number(offererId)
      )

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

  const [isWithdrawalMailDialogOpen, setIsWithdrawalMailDialogOpen] =
    useState<boolean>(false)

  const [sendWithdrawalMail, setSendWithdrawalMail] = useState<boolean>(false)

  const onSubmit = async (
    formValues: IndividualOfferFormValues
  ): Promise<void> => {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      const hasWithdrawalInformationsChanged = [
        'withdrawalDetails',
        'withdrawalDelay',
        'withdrawalType',
      ].some((field) => {
        const fieldMeta = formik.getFieldMeta(field)
        return (
          fieldMeta?.touched && fieldMeta?.value !== fieldMeta?.initialValue
        )
      })

      const showWithdrawalMailDialog =
        offer?.isActive &&
        offer.bookingsCount > 0 &&
        hasWithdrawalInformationsChanged
      if (showWithdrawalMailDialog && !isWithdrawalMailDialogOpen) {
        setIsWithdrawalMailDialogOpen(true)
        return
      }
    }

    // Submit
    const { isOk, payload } = !offer
      ? await createIndividualOffer(formValues)
      : await updateIndividualOffer({
          serializedOffer: serializePatchOffer({
            offer,
            formValues,
            shouldSendMail: sendWithdrawalMail,
          }),
          offerId: offer.id,
        })

    if (!isOk) {
      formik.setErrors(payload.errors)
      // This is used from scroll to error
      formik.setStatus('apiError')
      return
    }

    const receivedOfferId = payload.id
    await handleImageOnSubmit(receivedOfferId)

    // replace url to fix back button
    navigate(
      getIndividualOfferUrl({
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        offerId: receivedOfferId,
        mode,
      }),
      { replace: true }
    )

    setIsEvent(
      subCategories.find(
        (subcategory) => subcategory.id === formik.values.subcategoryId
      )?.isEvent
    )
    const nextStep =
      mode === OFFER_WIZARD_MODE.EDITION
        ? OFFER_WIZARD_STEP_IDS.SUMMARY
        : isEvent
          ? OFFER_WIZARD_STEP_IDS.TARIFS
          : OFFER_WIZARD_STEP_IDS.STOCKS

    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      to: nextStep,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode === OFFER_WIZARD_MODE.CREATION,
      offerId: receivedOfferId,
      subcategoryId: formik.values.subcategoryId,
    })

    navigate(
      getIndividualOfferUrl({
        offerId: receivedOfferId,
        step: nextStep,
        mode:
          mode === OFFER_WIZARD_MODE.EDITION
            ? OFFER_WIZARD_MODE.READ_ONLY
            : mode,
      })
    )

    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(PATCH_SUCCESS_MESSAGE)
    }
  }

  const readOnlyFields = setFormReadOnlyFields(offer, currentUser.isAdmin)
  const validationSchema = getValidationSchema(offer?.lastProvider?.name)
  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
    // enableReinitialize is needed to reset dirty after submit (and not block after saving a draft)
    enableReinitialize: true,
  })

  const handlePreviousStepOrBackToReadOnly = () => {
    const queryParams = new URLSearchParams(location.search)
    const queryOffererId = queryParams.get('structure')
    const queryVenueId = queryParams.get('lieu')

    /* istanbul ignore next: DEBT, TO FIX */
    mode === OFFER_WIZARD_MODE.EDITION
      ? navigate(
          getIndividualOfferUrl({
            offerId: offer?.id,
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })
        )
      : navigate({
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
            isEvent={isOfferSubtypeEvent(offerSubtype)}
          />

          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={OFFER_WIZARD_STEP_IDS.INFORMATIONS}
            isDisabled={
              formik.isSubmitting ||
              Boolean(offer && isOfferDisabled(offer.status)) ||
              isWithdrawalMailDialogOpen
            }
            dirtyForm={formik.dirty}
          />
        </form>
      </FormLayout>

      {isWithdrawalMailDialogOpen && (
        <ConfirmDialog
          cancelText="Ne pas envoyer"
          confirmText="Envoyer un email"
          onCancel={() => {
            setIsWithdrawalMailDialogOpen(false)
          }}
          leftButtonAction={async () => {
            await formik.submitForm()
          }}
          onConfirm={async () => {
            setSendWithdrawalMail(true)
            await formik.submitForm()
          }}
          icon={strokeMailIcon}
          title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
        />
      )}
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}

export default InformationsScreen
