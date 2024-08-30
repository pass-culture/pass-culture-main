import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  GetIndividualOfferResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
} from 'apiClient/v1'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { GET_OFFER_QUERY_KEY, GET_VENUES_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import strokeMailIcon from 'icons/stroke-mail.svg'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import { ActionBar } from '../ActionBar/ActionBar'
import { serializePatchOffer } from '../InformationsScreen/serializePatchOffer'

import { UsefulInformationFormValues } from './types'
import { UsefulInformationForm } from './UsefulInformationForm'
import { setDefaultInitialValuesFromOffer } from './utils'
import { getValidationSchema } from './validationSchema'

export const LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED =
  'USEFUL_INFORMATION_SUBMITTED'

export type UsefulInformationScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

const getLocalStorageKeyName = (offer: GetIndividualOfferResponseModel) =>
  `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer.id}`

export const UsefulInformationScreen = ({
  offer,
}: UsefulInformationScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const notify = useNotification()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const { subCategories } = useIndividualOfferContext()
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const [isWithdrawalMailDialogOpen, setIsWithdrawalMailDialogOpen] =
    useState<boolean>(false)

  const [sendWithdrawalMail, setSendWithdrawalMail] = useState<boolean>(false)

  const isEvent = subCategories.find(
    (subcategory) => subcategory.id === offer.subcategoryId
  )?.isEvent

  const addToLocalStorage = () => {
    const keyName = getLocalStorageKeyName(offer)
    if (localStorageAvailable() && localStorage.getItem(keyName) === null) {
      localStorage.setItem(keyName, true.toString())
    }
  }

  const onSubmit = async (
    formValues: UsefulInformationFormValues
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
        offer.isActive &&
        (offer.bookingsCount ?? 0) > 0 &&
        hasWithdrawalInformationsChanged
      if (showWithdrawalMailDialog && !isWithdrawalMailDialogOpen) {
        setIsWithdrawalMailDialogOpen(true)
        return
      }
    }

    try {
      const response = await api.patchOffer(
        offer.id,
        serializePatchOffer({
          offer,
          formValues,
          shouldSendMail: sendWithdrawalMail,
        })
      )

      const receivedOfferId = response.id
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
          : isEvent
            ? OFFER_WIZARD_STEP_IDS.TARIFS
            : OFFER_WIZARD_STEP_IDS.STOCKS

      addToLocalStorage()

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

    if (
      localStorageAvailable() &&
      localStorage.getItem(getLocalStorageKeyName(offer)) !== null &&
      formik.dirty
    ) {
      notify.success(PATCH_SUCCESS_MESSAGE)
    }
  }

  // Getting selected venue at step 1 (details) to infer address fields
  const venuesQuery = useSWR(
    [GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id],
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )

  const selectedVenue = venuesQuery.data.venues.find(
    (v) => v.id.toString() === offer.venue.id.toString()
  )

  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const conditionalFields = getOfferConditionalFields({
    offerSubCategory,
    isUserAdmin: false,
    receiveNotificationEmails: true,
    isVenueVirtual: offer.venue.isVirtual,
  })

  const validationSchema = getValidationSchema({
    subcategories: conditionalFields,
    isOfferAddressEnabled,
  })
  const formik = useFormik({
    initialValues: setDefaultInitialValuesFromOffer(offer, { selectedVenue }),
    onSubmit,
    validationSchema,
  })

  const handlePreviousStepOrBackToReadOnly = () => {
    mode === OFFER_WIZARD_MODE.CREATION
      ? navigate(
          getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.DETAILS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })
        )
      : navigate(
          getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })
        )
  }

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
          <ScrollToFirstErrorAfterSubmit />
          <FormLayout.MandatoryInfo />
          <UsefulInformationForm
            offer={offer}
            selectedVenue={selectedVenue}
            conditionalFields={conditionalFields}
          />
        </FormLayout>
        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS}
          isDisabled={formik.isSubmitting || isOfferDisabled(offer.status)}
          dirtyForm={formik.dirty}
        />
      </Form>
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
