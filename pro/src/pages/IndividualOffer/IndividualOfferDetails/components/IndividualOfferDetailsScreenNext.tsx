import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient//api'
import { isErrorAPIError } from '@/apiClient//helpers'
import type {
  GetIndividualOfferResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient//v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { getIndividualOfferImage } from '@/components/IndividualOffer/utils/getIndividualOfferImage'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { isRecordStore } from '@/pages/IndividualOffer/commons/isRecordStore'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import type {
  DetailsFormValues,
  Product,
} from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/useIndividualOfferImageUpload'
import {
  filterAvailableVenues,
  getFormReadOnlyFields,
  getInitialValuesFromOffer,
  getInitialValuesFromVenues,
  getVenuesAsOptions,
  hasMusicType,
} from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { getValidationSchemaForNewOfferCreationFlow } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'

import {
  serializeDetailsPatchData,
  serializeDetailsPostData,
} from '../commons/serializers'
import { DetailsEanSearch } from './DetailsEanSearch/DetailsEanSearch'
import { DetailsForm } from './DetailsForm/DetailsForm'
import { EanSearchCallout } from './EanSearchCallout/EanSearchCallout'

export type IndividualOfferDetailsScreenNextProps = {
  venues: VenueListItemResponseModel[]
}

export const IndividualOfferDetailsScreenNext = ({
  venues,
}: IndividualOfferDetailsScreenNextProps): JSX.Element => {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const mode = useOfferWizardMode()
  const isMediaPageEnabled = useActiveFeature('WIP_ADD_VIDEO')

  const {
    categories,
    subCategories,
    offer: initialOffer,
    publishedOfferWithSameEAN,
  } = useIndividualOfferContext()
  const initialOfferImage = getIndividualOfferImage(initialOffer)
  const {
    displayedImage,
    hasUpsertedImage,
    onImageDelete,
    onImageUpload,
    handleEanImage,
    handleImageOnSubmit,
  } = useIndividualOfferImageUpload(initialOfferImage)

  const isNewOfferDraft = !initialOffer
  const isNewOfferCreationFlowFeatureActive = true
  const availableVenues = filterAvailableVenues(venues)
  const availableVenuesAsOptions = getVenuesAsOptions(availableVenues)

  const initialValues = isNewOfferDraft
    ? getInitialValuesFromVenues(
        availableVenues,
        isNewOfferCreationFlowFeatureActive
      )
    : getInitialValuesFromOffer({
        offer: initialOffer,
        subcategories: subCategories,
        isNewOfferCreationFlowFeatureActive,
      })
  const form = useForm<DetailsFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver<DetailsFormValues>(
      getValidationSchemaForNewOfferCreationFlow()
    ),
    mode: 'onBlur',
  })

  const hasSelectedProduct = !!form.watch('productId')
  const selectedSubcategoryId = form.watch('subcategoryId')
  const isEanSearchAvailable = isRecordStore(availableVenues)
  const isEanSearchInputDisplayed =
    isEanSearchAvailable && mode === OFFER_WIZARD_MODE.CREATION
  const isEanSearchCalloutDisplayed =
    isEanSearchAvailable && mode === OFFER_WIZARD_MODE.EDITION
  const readOnlyFields = getFormReadOnlyFields(
    initialOffer,
    hasSelectedProduct,
    isNewOfferCreationFlowFeatureActive
  )

  const onSubmit = async (formValues: DetailsFormValues): Promise<void> => {
    try {
      // Draft offer PATCH requests are useless for product-based offers
      // and synchronized / provider offers since neither of the inputs displayed in
      // DetailsScreen can be edited at all
      const shouldNotPatchData =
        isOfferSynchronized(initialOffer) ||
        (!isNewOfferDraft && hasSelectedProduct)
      const initialOfferId = initialOffer?.id

      let response: GetIndividualOfferResponseModel | undefined
      let offerId = initialOfferId

      if (isNewOfferDraft) {
        response = await api.postDraftOffer(
          serializeDetailsPostData(
            formValues,
            isNewOfferCreationFlowFeatureActive
          )
        )
      } else if (!shouldNotPatchData && initialOfferId) {
        response = await api.patchDraftOffer(
          initialOfferId,
          serializeDetailsPatchData(
            formValues,
            isNewOfferCreationFlowFeatureActive
          )
        )
      }

      offerId = response?.id ?? initialOfferId

      // Images can never be uploaded for product-based offers,
      // the drag & drop should not be displayed / enabled so
      // this is a safeguard.
      if (!isMediaPageEnabled && !!offerId && !hasSelectedProduct) {
        await handleImageOnSubmit(offerId)
        await mutate([GET_OFFER_QUERY_KEY, offerId])
      }

      // replace url to fix back button
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          offerId,
          mode,
          isOnboarding: pathname.indexOf('onboarding') !== -1,
        }),
        { replace: true }
      )
      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
        offerId,
        venueId: form.getValues('venueId'),
        offerType: 'individual',
        subcategoryId: form.getValues('subcategoryId'),
      })
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId,
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
        form.setError(field as keyof DetailsFormValues, {
          message: error.body[field],
        })
      }
    }
  }

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(`${isOnboarding ? '/onboarding' : ''}/offre/creation`)
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: initialOffer?.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
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

    const subCategory = subCategories.find(
      (subCategory) => subCategory.id === subcategoryId
    )

    if (!subCategory) {
      throw new Error('Unknown or missing subcategoryId')
    }

    const { categoryId, conditionalFields } = subCategory

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
          initialEan={initialOffer?.extraData?.ean}
          isProductBased={hasSelectedProduct}
          onEanReset={resetFormAndEanImage}
          onEanSearch={updateProduct}
          subcategoryId={selectedSubcategoryId}
        />
      )}
      {isEanSearchCalloutDisplayed && <EanSearchCallout isDraftOffer={false} />}

      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FormLayout fullWidthActions>
            <ScrollToFirstHookFormErrorAfterSubmit />
            <DetailsForm
              displayedImage={displayedImage}
              filteredCategories={categories}
              filteredSubcategories={subCategories}
              hasSelectedProduct={hasSelectedProduct}
              isEanSearchDisplayed={isEanSearchInputDisplayed}
              onImageDelete={onImageDelete}
              onImageUpload={onImageUpload}
              readOnlyFields={readOnlyFields}
              venues={venues}
              venuesOptions={availableVenuesAsOptions}
            />
          </FormLayout>

          <ActionBar
            dirtyForm={form.formState.isDirty || isNewOfferDraft}
            isDisabled={
              form.formState.isSubmitting ||
              Boolean(initialOffer && isOfferDisabled(initialOffer.status)) ||
              Boolean(publishedOfferWithSameEAN)
            }
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS}
          />
        </form>
      </FormProvider>

      <RouteLeavingGuardIndividualOffer
        when={
          (form.formState.isDirty ||
            (!isMediaPageEnabled && hasUpsertedImage)) &&
          !form.formState.isSubmitting
        }
      />
    </>
  )
}
