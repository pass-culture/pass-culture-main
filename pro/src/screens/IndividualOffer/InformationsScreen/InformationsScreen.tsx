import { FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { IndividualOfferForm } from 'components/IndividualOfferForm/IndividualOfferForm'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { getFilteredVenueListByCategoryStatus } from 'components/IndividualOfferForm/utils/getFilteredVenueList'
import { setDefaultInitialFormValues } from 'components/IndividualOfferForm/utils/setDefaultInitialFormValues'
import { setFormReadOnlyFields } from 'components/IndividualOfferForm/utils/setFormReadOnlyFields'
import { setInitialFormValues } from 'components/IndividualOfferForm/utils/setInitialFormValues'
import { getValidationSchema } from 'components/IndividualOfferForm/validationSchema'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { GET_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useNotification } from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import strokeMailIcon from 'icons/stroke-mail.svg'
import { selectCurrentOffererId } from 'store/user/selectors'

import { ActionBar } from '../ActionBar/ActionBar'
import { useIndividualOfferImageUpload } from '../hooks/useIndividualOfferImageUpload'

import { serializePatchOffer } from './serializePatchOffer'
import { serializePostOffer } from './serializePostOffer'
import {
  filterCategories,
  getCategoryStatusFromOfferSubtype,
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from './utils/filterCategories/filterCategories'

export interface InformationsScreenProps {
  offererId: string | null
  venueId: string | null
  offererNames: GetOffererNameResponseModel[]
  venueList: VenueListItemResponseModel[]
}

export const InformationsScreen = ({
  offererId,
  venueId,
  offererNames,
  venueList,
}: InformationsScreenProps): JSX.Element => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const { offer, categories, subCategories } = useIndividualOfferContext()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useIndividualOfferImageUpload()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const queryParams = new URLSearchParams(location.search)
  const queryOfferType = queryParams.get('offer-type')

  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  const categoryStatus = getCategoryStatusFromOfferSubtype(offerSubtype)
  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    categoryStatus,
    isOfferSubtypeEvent(offerSubtype)
  )

  const filteredVenueList = getFilteredVenueListByCategoryStatus(
    venueList,
    categoryStatus
  ).filter((venue) => venue.managingOffererId === Number(offererId))

  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  // offer is null when we are creating a new offer
  const initialValues: IndividualOfferFormValues =
    offer === null
      ? setDefaultInitialFormValues(
          offererNames,
          offererId,
          venueId,
          filteredVenueList,
          true,
          offerAddressEnabled
        )
      : setInitialFormValues(offer, subCategories, true)

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
        return fieldMeta.touched && fieldMeta.value !== fieldMeta.initialValue
      })

      const showWithdrawalMailDialog =
        offer?.isActive &&
        (offer.bookingsCount ?? 0) > 0 &&
        hasWithdrawalInformationsChanged
      if (showWithdrawalMailDialog && !isWithdrawalMailDialogOpen) {
        setIsWithdrawalMailDialogOpen(true)
        return
      }
    }

    // Submit
    try {
      const response = !offer
        ? await api.postOffer(serializePostOffer(formValues))
        : await api.patchOffer(
            offer.id,
            serializePatchOffer({
              offer,
              formValues,
              shouldSendMail: sendWithdrawalMail,
            })
          )

      const receivedOfferId = response.id
      await handleImageOnSubmit(receivedOfferId)
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

      // replace url to fix back button
      navigate(
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          offerId: receivedOfferId,
          mode,
        }),
        { replace: true }
      )
      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.SUMMARY
          : isEvent
            ? OFFER_WIZARD_STEP_IDS.TARIFS
            : OFFER_WIZARD_STEP_IDS.STOCKS

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        to: nextStep,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode === OFFER_WIZARD_MODE.CREATION,
        offerId: receivedOfferId,
        offerType: 'individual',
        subcategoryId: formik.values.subcategoryId,
        offererId: selectedOffererId?.toString(),
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
    } catch (error) {
      if (!isErrorAPIError(error)) {
        return
      }
      formik.setErrors(
        serializeApiErrors(error.body, {
          venue: 'venueId',
        })
      )
      // This is used from scroll to error
      formik.setStatus('apiError')
    }

    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(PATCH_SUCCESS_MESSAGE)
    }
  }

  const readOnlyFields = setFormReadOnlyFields(offer, currentUser.isAdmin)
  const DONT_USE_OFFER_LOCATION_SCHEMA = !offerAddressEnabled
  const validationSchema = getValidationSchema(
    offer?.lastProvider?.name,
    DONT_USE_OFFER_LOCATION_SCHEMA
  )
  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
    // enableReinitialize is needed to reset dirty after submit (and not block after saving a draft)
    enableReinitialize: true,
  })

  const isEvent =
    subCategories.find(
      (subcategory) => subcategory.id === formik.values.subcategoryId
    )?.isEvent ?? isOfferSubtypeEvent(offerSubtype)

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
      <FormLayout fullWidthActions>
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
            isEvent={isEvent}
          />

          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={OFFER_WIZARD_STEP_IDS.INFORMATIONS}
            isDisabled={
              formik.isSubmitting ||
              Boolean(offer && isOfferDisabled(offer.status)) ||
              isWithdrawalMailDialogOpen
            }
            dirtyForm={formik.dirty || offer === null}
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
