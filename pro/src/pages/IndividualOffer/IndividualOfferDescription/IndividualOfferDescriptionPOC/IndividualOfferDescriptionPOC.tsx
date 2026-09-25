import { useRef } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import useSWR, { mutate } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import {
  isOfferProductBasedButNotSynchronized,
  isOfferSynchronized,
} from '@/commons/core/Offers/utils/typology'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { API_URL } from '@/commons/utils/config'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'

import { getAfterSubmitPath } from '../../commons/utils/getAfterSubmitPath'
import { ActionBar } from '../../components/ActionBar/ActionBar'
import { ProductBanner } from '../../components/ProductBanner/ProductBanner'
import { SynchronizedBanner } from '../../components/SynchronizedBanner/SynchronizedBanner'
import {
  serializeDetailsPatchData,
  serializeDetailsPostData,
} from '../commons/serializers'
import type { DetailsFormValues } from '../commons/types'
import { getInitialValuesFromVenue } from '../commons/utils'
import type { NfdOfferFormResponse } from '../components/NfdOfferForm/types'
import { DetailsFormPOC } from './DetailsFormPOC'

const getNfdOfferForm = async (): Promise<NfdOfferFormResponse> => {
  const response = await fetch(`${API_URL}/offers/nfd-form-preview`, {
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error('Unable to retrieve NFD offer form')
  }

  return response.json() as Promise<NfdOfferFormResponse>
}

export const IndividualOfferDescriptionPOC = () => {
  const { offer: initialOffer, hasPublishedOfferWithSameEan } =
    useIndividualOfferContext()
  const offerIdRef = useRef(initialOffer?.id)
  const { data: nfdOfferForm } = useSWR(
    '/offers/nfd-form-preview',
    getNfdOfferForm
  )
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const mode = useOfferWizardMode()
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const hasSavedOfferRef = useRef(false)
  const navigate = useNavigate()

  const onSubmit = async (formValues: DetailsFormValues): Promise<boolean> => {
    try {
      if (offerIdRef.current) {
        await mutate(
          [GET_OFFER_QUERY_KEY, offerIdRef.current],
          api.patchOffer({
            path: { offer_id: offerIdRef.current },
            body: serializeDetailsPatchData(formValues),
          }),
          { revalidate: false }
        )
      } else {
        await mutate(
          [GET_OFFER_QUERY_KEY],
          api.createOffer({ body: serializeDetailsPostData(formValues) }),
          {
            revalidate: false,
            populateCache: (newOffer) => {
              offerIdRef.current = newOffer.id
              return newOffer
            },
          }
        )

        // Replace current history entry so that it points to this new offer ID when clicking the browser back button
        globalThis.history.replaceState(
          globalThis.history.state,
          '',
          getIndividualOfferUrl({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
            offerId: offerIdRef.current,
            mode: OFFER_WIZARD_MODE.CREATION,
            isOnboarding,
          })
        )
      }

      if (mode === OFFER_WIZARD_MODE.EDITION) {
        hasSavedOfferRef.current = true
      }

      return true
    } catch (error) {
      if (isErrorAPIError(error)) {
        for (const field in error.body) {
          form.setError(field as keyof DetailsFormValues, {
            message: error.body[field],
          })
        }
      }

      return false
    }
  }

  const getInitialValues = () => {
    return getInitialValuesFromVenue(selectedPartnerVenue)
  }

  const handlePreviousStep = () => {
    navigate(isOnboarding ? '/onboarding/individuel' : '/offre/creation')
  }

  const form = useForm<DetailsFormValues>({
    defaultValues: getInitialValues(),
    mode: 'onBlur',
  })

  const afterSubmitPath = () =>
    getAfterSubmitPath({
      offerId: offerIdRef.current,
      mode,
      isOnboarding,
      followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
    })
  const afterSubmitState = () =>
    hasSavedOfferRef.current
      ? { successMessage: 'Votre offre a bien été modifiée.' }
      : undefined

  const { navigationGuardedSubmitHandler, navigationGuardDialog } =
    useFormNavigationGuard({
      afterSubmitPath,
      afterSubmitState,
      form,
      onSubmit,
    })

  return (
    <>
      {isOfferProductBasedButNotSynchronized(initialOffer) && <ProductBanner />}
      {isOfferSynchronized(initialOffer) && (
        <SynchronizedBanner providerName={initialOffer?.lastProvider?.name} />
      )}
      <FormLayout.MandatoryInfo />
      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <FormLayout fullWidthActions>
            <ScrollToFirstHookFormErrorAfterSubmit />
            <DetailsFormPOC
              formDefinition={nfdOfferForm?.formDefinition ?? []}
            />
          </FormLayout>

          <ActionBar
            dirtyForm={form.formState.isDirty}
            isDisabled={
              form.formState.isSubmitting ||
              Boolean(initialOffer && isOfferDisabled(initialOffer)) ||
              hasPublishedOfferWithSameEan ||
              (!form.formState.isDirty && mode !== OFFER_WIZARD_MODE.CREATION)
            }
            onClickPrevious={handlePreviousStep}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION}
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
