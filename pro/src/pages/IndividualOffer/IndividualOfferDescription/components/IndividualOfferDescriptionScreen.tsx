import { yupResolver } from '@hookform/resolvers/yup'
import { useRef } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { DisplayableActivity } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  CULTURAL_OUTREACH_ALLOWED_ACTIVITIES,
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import type { OfferExtraData } from '@/commons/core/Offers/types'
import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { getAfterSubmitPath } from '@/pages/IndividualOffer/commons/utils/getAfterSubmitPath'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import type {
  DetailsFormValues,
  Product,
} from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/useIndividualOfferImageUpload'
import {
  getFormReadOnlyFields,
  getInitialValuesFromOffer,
  getInitialValuesFromVenue,
  hasMusicType,
} from '@/pages/IndividualOffer/IndividualOfferDescription/commons/utils'
import { getValidationSchema } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/validationSchema'

import {
  serializeDetailsPatchData,
  serializeDetailsPostData,
} from '../commons/serializers'
import { DetailsEanSearch } from './DetailsEanSearch/DetailsEanSearch'
import { DetailsForm } from './DetailsForm/DetailsForm'
import { EanSearchCallout } from './EanSearchCallout/EanSearchCallout'

export const IndividualOfferDescriptionScreen = () => {
  const isCulturalOutreachEnabled = useActiveFeature(
    'WIP_ENABLE_CULTURAL_OUTREACH'
  )
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  const {
    categories,
    subCategories,
    offer: initialOffer,
    hasPublishedOfferWithSameEan,
  } = useIndividualOfferContext()
  const offerIdRef = useRef(initialOffer?.id)

  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const mode = useOfferWizardMode()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const snackBar = useSnackBar()

  const initialOfferImage = getIndividualOfferImage(initialOffer)
  const extraData = initialOffer?.extraData as OfferExtraData | undefined
  const { handleEanImage } = useIndividualOfferImageUpload(initialOfferImage)

  const isNewOfferDraft = !initialOffer

  const getInitialValues = () => {
    return isNewOfferDraft
      ? getInitialValuesFromVenue(selectedPartnerVenue)
      : getInitialValuesFromOffer({
          offer: initialOffer,
          subcategories: subCategories,
        })
  }

  const form = useForm<DetailsFormValues>({
    defaultValues: getInitialValues(),
    resolver: yupResolver<DetailsFormValues, unknown, unknown>(
      // @ts-expect-error - Waiting for pydanticV2 migration
      getValidationSchema()
    ),
    mode: 'onBlur',
  })

  const hasSelectedProduct = !!form.watch('productId')

  const selectedSubcategoryId = form.watch('subcategoryId')

  const isEanSearchAvailable =
    selectedPartnerVenue.activity === DisplayableActivity.RECORD_STORE

  const canClaimCulturalOutreach =
    isCulturalOutreachEnabled &&
    selectedPartnerVenue.activity !== null &&
    CULTURAL_OUTREACH_ALLOWED_ACTIVITIES.has(selectedPartnerVenue.activity)

  const isEanSearchInputDisplayed =
    isEanSearchAvailable && mode === OFFER_WIZARD_MODE.CREATION

  const isEanSearchCalloutDisplayed =
    isEanSearchAvailable && mode === OFFER_WIZARD_MODE.EDITION

  const readOnlyFields = getFormReadOnlyFields(
    initialOffer,
    hasSelectedProduct,
    selectedPartnerVenue
  )

  const onSubmit = async (formValues: DetailsFormValues): Promise<boolean> => {
    try {
      if (offerIdRef.current) {
        await mutate(
          [GET_OFFER_QUERY_KEY, offerIdRef.current],
          api.patchOffer({
            path: { offer_id: offerIdRef.current },
            body: serializeDetailsPatchData(formValues, readOnlyFields),
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

      if (isOfferExposureEnabled && mode === OFFER_WIZARD_MODE.EDITION) {
        snackBar.success('Votre offre a bien été modifiée.')
      }

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        offerId: offerIdRef.current,
        offerType: 'individual',
        subcategoryId: form.getValues('subcategoryId'),
      })

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

  const afterSubmitPath = () =>
    getAfterSubmitPath({
      offerId: offerIdRef.current,
      mode,
      isOnboarding,
      isOfferExposureEnabled,
      currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
      followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
    })
  const { navigationGuardedSubmitHandler, navigationGuardDialog } =
    useFormNavigationGuard({
      afterSubmitPath,
      form,
      onSubmit,
    })

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      navigate(isOnboarding ? '/onboarding/individuel' : '/offre/creation')
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: offerIdRef.current,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
          isOfferExposureEnabled,
        })
      )
    }
  }

  const updateProduct = (ean: string, product: Product) => {
    const {
      id,
      name,
      description,
      subcategoryId,
      gtlId,
      author,
      performer,
      images,
    } = product

    const subcategory = subCategories.find((s) => s.id === subcategoryId)
    if (!subcategory) {
      return handleUnexpectedError(
        new FrontendError('Unknown or missing `subcategoryId`.')
      )
    }

    const { categoryId, conditionalFields } = subcategory

    const imageUrl = images.recto
    if (imageUrl) {
      handleEanImage(imageUrl)
    }

    let gtl_id = ''
    if (hasMusicType(categoryId, conditionalFields)) {
      // Fallback to "Autre" in case of missing gtlId
      // to define "Genre musical" when relevant.
      gtl_id = gtlId || '19000000'
    }

    form.setValue('ean', ean)
    form.setValue('name', name)
    form.setValue('description', description || '')
    form.setValue('categoryId', categoryId)
    form.setValue('subcategoryId', subcategoryId)
    form.setValue('gtl_id', gtl_id)
    form.setValue('author', author)
    form.setValue('artistOfferLinks', [])
    form.setValue('performer', performer)
    form.setValue(
      'subcategoryConditionalFields',
      conditionalFields as Array<keyof DetailsFormValues>
    )
    form.setValue('productId', id.toString())
  }

  const resetFormAndEanImage = () => {
    handleEanImage()
    form.reset()
  }

  return (
    <>
      <FormLayout.MandatoryInfo />

      {isEanSearchInputDisplayed && (
        <DetailsEanSearch
          isDraftOffer={isNewOfferDraft}
          initialEan={extraData?.ean}
          isProductBased={hasSelectedProduct}
          onEanReset={resetFormAndEanImage}
          onEanSearch={updateProduct}
          subcategoryId={selectedSubcategoryId}
        />
      )}
      {isEanSearchCalloutDisplayed && <EanSearchCallout isDraftOffer={false} />}

      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <FormLayout fullWidthActions>
            <ScrollToFirstHookFormErrorAfterSubmit />
            <DetailsForm
              filteredCategories={categories}
              filteredSubcategories={subCategories}
              hasSelectedProduct={hasSelectedProduct}
              isEanSearchDisplayed={isEanSearchInputDisplayed}
              readOnlyFields={readOnlyFields}
              canClaimCulturalOutreach={canClaimCulturalOutreach}
            />
          </FormLayout>

          <ActionBar
            dirtyForm={form.formState.isDirty || isNewOfferDraft}
            isDisabled={
              form.formState.isSubmitting ||
              Boolean(initialOffer && isOfferDisabled(initialOffer)) ||
              hasPublishedOfferWithSameEan ||
              (isOfferExposureEnabled &&
                !form.formState.isDirty &&
                mode !== OFFER_WIZARD_MODE.CREATION)
            }
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION}
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
