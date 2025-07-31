import { yupResolver } from '@hookform/resolvers/yup'
import { useRef, useState, useEffect } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  GetIndividualOfferResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
} from 'apiClient/v1'
import {
  GET_OFFER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  OFFER_WIZARD_MODE,
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { SENT_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { usePrevious } from 'commons/hooks/usePrevious'
import { getOfferConditionalFields } from 'commons/utils/getOfferConditionalFields'
import { isEqual } from 'commons/utils/isEqual'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { serializePatchOffer } from 'pages/IndividualOffer/IndividualOfferInformations/commons/serializers'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

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

  const saveEditionChangesButtonRef = useRef<HTMLButtonElement>(null)

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
  const isMediaPageEnabled = useActiveFeature('WIP_ADD_VIDEO')
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const addToLocalStorage = () => {
    const keyName = getLocalStorageKeyName(offer)
    if (
      storageAvailable('localStorage') &&
      localStorage.getItem(keyName) === null
    ) {
      localStorage.setItem(keyName, true.toString())
    }
  }

  const onSubmit = async (): Promise<void> => {
    const formValues = form.getValues()

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
      const requestBody = serializePatchOffer({
        offer,
        formValues,
        shouldSendMail: sendWithdrawalMail,
        isNewOfferCreationFlowFeatureActive,
      })
      const response = await api.patchOffer(offer.id, requestBody)

      const receivedOfferId = response.id
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

      const nextStepForEdition =
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
      const nextStepForCreation = isMediaPageEnabled
        ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
        : isEvent
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS

      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? nextStepForEdition
          : nextStepForCreation

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

      for (const field in error.body) {
        form.setError(field as keyof UsefulInformationFormValues, {
          message: error.body[field],
        })
      }

      notify.error(SENT_DATA_ERROR_MESSAGE)
      return
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
    offerSubCategory,
  })
  const previousInitialValues = usePrevious(initialValues)
  const initialValuesHasChanged = !isEqual(previousInitialValues, initialValues)

  // Workaround since react-hook-form does not reset the form when defaultValues change.
  useEffect(() => {
    if (initialValuesHasChanged) {
      form.reset(initialValues)
    }
  }, [initialValuesHasChanged])

  const form = useForm<UsefulInformationFormValues>({
    defaultValues: initialValues,
    mode: 'all',
    resolver: yupResolver(validationSchema),
  })

  const someFormFieldsChanged = (
    fields: (keyof UsefulInformationFormValues)[]
  ): boolean => {
    return fields.some((field) => {
      const fieldState = form.getFieldState(field)
      const fieldValue = form.getValues(field)

      return fieldState.isTouched && fieldValue !== initialValues[field]
    })
  }

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })
      )
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
    }
  }

  return (
    <>
      <ConfirmDialog
        cancelText="Annuler"
        confirmText="Je confirme le changement"
        onCancel={() => {
          setIsUpdatesWarningDialogOpen(false)
        }}
        onConfirm={form.handleSubmit(onSubmit)}
        open={isUpdatesWarningDialogOpen}
        title="Les changements vont s’appliquer à l’ensemble des réservations en cours associées"
        refToFocusOnClose={saveEditionChangesButtonRef}
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
              label="Prévenir les jeunes par e-mail"
              onChange={(evt) => setSendWithdrawalMail(evt.target.checked)}
              checked={sendWithdrawalMail}
            />
          </FormLayout.Row>
        </div>
      </ConfirmDialog>

      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <ScrollToFirstHookFormErrorAfterSubmit />
          <FormLayout fullWidthActions>
            <FormLayout.MandatoryInfo />
            <UsefulInformationForm
              selectedVenue={selectedVenue}
              conditionalFields={conditionalFields}
              publishedOfferWithSameEAN={publishedOfferWithSameEAN}
            />
          </FormLayout>
          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS}
            isDisabled={
              form.formState.isSubmitting ||
              isOfferDisabled(offer.status) ||
              Boolean(publishedOfferWithSameEAN)
            }
            dirtyForm={form.formState.isDirty}
            saveEditionChangesButtonRef={saveEditionChangesButtonRef}
          />
        </form>
      </FormProvider>

      <RouteLeavingGuardIndividualOffer
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </>
  )
}
