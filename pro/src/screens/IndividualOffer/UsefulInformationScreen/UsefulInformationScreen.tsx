import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
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
  offer: GetIndividualOfferResponseModel
}

export const UsefulInformationScreen = ({
  offer,
}: UsefulInformationScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const { subCategories } = useIndividualOfferContext()

  const [isWithdrawalMailDialogOpen, setIsWithdrawalMailDialogOpen] =
    useState<boolean>(false)

  const [sendWithdrawalMail, setSendWithdrawalMail] = useState<boolean>(false)

  const isEvent = subCategories.find(
    (subcategory) => subcategory.id === offer.subcategoryId
  )?.isEvent

  const addToLocalStorage = () => {
    const keyName = `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer.id}`
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

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
        to: nextStep,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode === OFFER_WIZARD_MODE.CREATION,
        offerId: receivedOfferId,
        offerType: 'individual',
        subcategoryId: offer.subcategoryId,
      })

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

    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(PATCH_SUCCESS_MESSAGE)
    }
  }

  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const conditionalFields = getOfferConditionalFields({
    offerSubCategory,
    isUserAdmin: false,
    receiveNotificationEmails: true,
    isVenueVirtual: offer.venue.isVirtual,
  })

  const validationSchema = getValidationSchema(conditionalFields)
  const formik = useFormik({
    initialValues: setDefaultInitialValuesFromOffer(offer),
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
