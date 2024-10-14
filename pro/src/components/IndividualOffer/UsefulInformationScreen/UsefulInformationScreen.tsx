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
import {
  GET_OFFER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { PATCH_SUCCESS_MESSAGE } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { getOfferConditionalFields } from 'commons/utils/getOfferConditionalFields'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import strokeMailIcon from 'icons/stroke-mail.svg'

import { ActionBar } from '../ActionBar/ActionBar'
import { serializePatchOffer } from '../InformationsScreen/serializePatchOffer'

import { UsefulInformationFormValues } from './types'
import { UsefulInformationForm } from './UsefulInformationForm/UsefulInformationForm'
import styles from './UsefulInformationScreen.module.scss'
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
  const isSearchByEanEnabled = useActiveFeature('WIP_EAN_CREATION')

  const [isWithdrawalMailDialogOpen, setIsWithdrawalMailDialogOpen] =
    useState<boolean>(false)
  const [isAddressUpdateDialogOpen, setIsAddressUpdateDialogOpen] =
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

  function someFormFieldsChanged(fields: string[]): boolean {
    return fields.some((field) => {
      const fieldMeta = formik.getFieldMeta(field)
      return fieldMeta.touched && fieldMeta.value !== fieldMeta.initialValue
    })
  }

  const onSubmit = async (
    formValues: UsefulInformationFormValues
  ): Promise<void> => {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      const hasWithdrawalInformationsChanged = someFormFieldsChanged([
        'withdrawalDetails',
        'withdrawalDelay',
        'withdrawalType',
      ])

      const hasAddressChanged = someFormFieldsChanged([
        'offerlocation',
        'locationLabel',
        'search-addressAutocomplete',
        'street',
        'postalCode',
        'city',
        'coords',
      ])

      const showWithdrawalMailDialog =
        offer.isActive &&
        (offer.bookingsCount ?? 0) > 0 &&
        hasWithdrawalInformationsChanged
      if (showWithdrawalMailDialog && !isWithdrawalMailDialogOpen) {
        setIsWithdrawalMailDialogOpen(true)
        return
      }

      const showAddressChangeDialog =
        offer.isActive && (offer.bookingsCount ?? 0) > 0 && hasAddressChanged
      if (showAddressChangeDialog && !isAddressUpdateDialogOpen) {
        setIsAddressUpdateDialogOpen(true)
        return
      }
    }

    try {
      const shouldNotSendExtraData = isSearchByEanEnabled && !!offer.productId
      const response = await api.patchOffer(
        offer.id,
        serializePatchOffer({
          offer,
          formValues,
          shouldSendMail: sendWithdrawalMail,
          shouldNotSendExtraData,
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

  const initialValues = setDefaultInitialValuesFromOffer({
    offer,
    selectedVenue,
  })

  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
    enableReinitialize: true,
  })
  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.CREATION,
        })
      )
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
        })
      )
    }
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
      <ConfirmDialog
        cancelText="Annuler"
        confirmText="Je confirme le changement"
        onCancel={() => {
          setIsAddressUpdateDialogOpen(false)
        }}
        onConfirm={async () => {
          await formik.submitForm()
        }}
        open={isAddressUpdateDialogOpen}
        title="Le changement d’adresse va s’impacter à l’ensemble des réservations en cours associées."
      >
        <div className={styles['update-oa-wrapper']}>
          <div>
            Un email va être envoyé aux bénéficiaires ayant réservé les offres
            concernées. Ils auront 48h pour annuler leur réservation s’ils le
            souhaitent.
          </div>
          <Callout variant={CalloutVariant.WARNING}>
            Si vous souhaitez que les réservations en cours conservent
            l’ancienne adresse, veuillez créer une nouvelle offre avec la
            nouvelle adresse.
          </Callout>
        </div>
      </ConfirmDialog>
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}
