import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router'
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
import { SENT_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { getOfferConditionalFields } from 'commons/utils/getOfferConditionalFields'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { serializePatchOffer } from 'pages/IndividualOffer/commons/serializers'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'

import { UsefulInformationFormValues } from '../commons/types'
import { setDefaultInitialValuesFromOffer } from '../commons/utils'
import { getValidationSchema } from '../commons/validationSchema'

import styles from './IndividualOfferInformationsScreen.module.scss'
import { UsefulInformationForm } from './UsefulInformationForm/UsefulInformationForm'

export const LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED =
  'USEFUL_INFORMATION_SUBMITTED'

export type IndividualOfferInformationsScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

const getLocalStorageKeyName = (offer: GetIndividualOfferResponseModel) =>
  `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer.id}`

export const IndividualOfferInformationsScreen = ({
  offer,
}: IndividualOfferInformationsScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const notify = useNotification()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const { subCategories, publishedOfferWithSameEAN } =
    useIndividualOfferContext()

  const [isUpdatesWarningDialogOpen, setIsUpdatesWarningDialogOpen] =
    useState(false)
  const [warningFieldsChanged, setWarningFieldsChanged] = useState<{
    address: boolean
    withdrawalInformations: boolean
  }>({ address: false, withdrawalInformations: false })

  const [sendWithdrawalMail, setSendWithdrawalMail] = useState<boolean>(true)

  const isEvent = subCategories.find(
    (subcategory) => subcategory.id === offer.subcategoryId
  )?.isEvent

  const addToLocalStorage = () => {
    const keyName = getLocalStorageKeyName(offer)
    if (
      storageAvailable('localStorage') &&
      localStorage.getItem(keyName) === null
    ) {
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
        'offerLocation',
        'search-addressAutocomplete',
        'street',
        'postalCode',
        'city',
        'coords',
      ])

      setWarningFieldsChanged((fields) => ({
        ...fields,
        address: hasAddressChanged,
        withdrawalInformations: hasWithdrawalInformationsChanged,
      }))

      const showUpdatesWarningModal =
        offer.hasPendingBookings &&
        (hasWithdrawalInformationsChanged || hasAddressChanged)

      if (showUpdatesWarningModal && !isUpdatesWarningDialogOpen) {
        setIsUpdatesWarningDialogOpen(true)
        return
      }
    }

    try {
      const shouldNotSendExtraData = !!offer.productId
      const requestBody = serializePatchOffer({
        offer,
        formValues,
        shouldSendMail: sendWithdrawalMail,
        shouldNotSendExtraData,
      })
      const response = await api.patchOffer(offer.id, requestBody)

      const receivedOfferId = response.id
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
          : isEvent
            ? OFFER_WIZARD_STEP_IDS.TARIFS
            : OFFER_WIZARD_STEP_IDS.STOCKS

      addToLocalStorage()

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: receivedOfferId,
          step: nextStep,
          mode:
            mode === OFFER_WIZARD_MODE.EDITION
              ? OFFER_WIZARD_MODE.READ_ONLY
              : mode,
          isOnboarding,
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

      return notify.error(SENT_DATA_ERROR_MESSAGE)
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
    receiveNotificationEmails: true,
  })

  const validationSchema = getValidationSchema({
    subcategories: conditionalFields,
    isDigitalOffer: offer.isDigital,
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
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })
      )
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
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
            publishedOfferWithSameEAN={publishedOfferWithSameEAN}
          />
        </FormLayout>
        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS}
          isDisabled={
            formik.isSubmitting ||
            isOfferDisabled(offer.status) ||
            Boolean(publishedOfferWithSameEAN)
          }
          dirtyForm={formik.dirty}
        />
      </Form>

      <ConfirmDialog
        cancelText="Annuler"
        confirmText="Je confirme le changement"
        onCancel={() => {
          setIsUpdatesWarningDialogOpen(false)
        }}
        onConfirm={async () => {
          await formik.submitForm()
        }}
        open={isUpdatesWarningDialogOpen}
        title="Les changements vont s’appliquer à l’ensemble des réservations en cours associées"
      >
        <div className={styles['update-oa-wrapper']}>
          <div>
            Vous avez modifié{' '}
            {warningFieldsChanged.address &&
            warningFieldsChanged.withdrawalInformations
              ? 'les modalités de retrait et la localisation'
              : warningFieldsChanged.address
                ? 'la localisation'
                : 'les modalités de retrait'}
            .
          </div>
          <Callout variant={CalloutVariant.WARNING}>
            Si vous souhaitez que les réservations en cours conservent les
            données actuelles, veuillez créer une nouvelle offre avec les
            nouvelles informations.
          </Callout>
          <FormLayout.Row>
            <Checkbox
              hideFooter
              label={'Prévenir les jeunes par e-mail'}
              name="shouldSendMail"
              onChange={(evt) => setSendWithdrawalMail(evt.target.checked)}
              checked={sendWithdrawalMail}
            />
          </FormLayout.Row>
        </div>
      </ConfirmDialog>
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}
