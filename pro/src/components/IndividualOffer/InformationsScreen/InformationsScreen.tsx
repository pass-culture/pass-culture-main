import { FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  CATEGORY_STATUS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { PATCH_SUCCESS_MESSAGE } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
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
import strokeMailIcon from 'icons/stroke-mail.svg'

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
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const { offer, categories, subCategories } = useIndividualOfferContext()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useIndividualOfferImageUpload()

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
  const isSearchByEanEnabled = useActiveFeature('WIP_EAN_CREATION')

  // TODO : Find a cleaner way to achieve this :
  // The only way to infer event type (physical or numeric) and make it works for both creation AND edition, is to check CATEGORY_STATUS or if an offer has a "url" (meaning that it's not physical)
  // (This is because CATEGORY_STATUS is always ONLINE_OR_OFFLINE for edition)
  const isPhysicalEvent =
    categoryStatus === CATEGORY_STATUS.OFFLINE || offer?.url === null

  // offer is null when we are creating a new offer
  const initialValues: IndividualOfferFormValues =
    offer === null
      ? setDefaultInitialFormValues(
          offererNames,
          offererId,
          venueId,
          filteredVenueList,
          true,
          offerAddressEnabled,
          isPhysicalEvent
        )
      : setInitialFormValues(
          offer,
          subCategories,
          true,
          offerAddressEnabled,
          isPhysicalEvent
        )

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
      const shouldNotSendExtraData = isSearchByEanEnabled && !!offer?.productId
      const response = !offer
        ? await api.postOffer(serializePostOffer(formValues))
        : await api.patchOffer(
            offer.id,
            serializePatchOffer({
              offer,
              formValues,
              shouldSendMail: sendWithdrawalMail,
              shouldNotSendExtraData,
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
  const ENABLE_OFFER_LOCATION_SCHEMA = offerAddressEnabled && isPhysicalEvent
  const validationSchema = getValidationSchema(
    offer?.lastProvider?.name,
    ENABLE_OFFER_LOCATION_SCHEMA
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
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer?.id,
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
        })
      )
    } else {
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
        open={isWithdrawalMailDialogOpen}
      />
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}
