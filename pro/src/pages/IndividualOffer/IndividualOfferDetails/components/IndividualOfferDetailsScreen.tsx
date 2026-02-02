import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { VenueListItemResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { FormLayout } from '@/components/FormLayout/FormLayout'
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
import { getValidationSchema } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'

import {
  serializeDetailsPatchData,
  serializeDetailsPostData,
} from '../commons/serializers'
import { DetailsEanSearch } from './DetailsEanSearch/DetailsEanSearch'
import { DetailsForm } from './DetailsForm/DetailsForm'
import { EanSearchCallout } from './EanSearchCallout/EanSearchCallout'

export type IndividualOfferDetailsScreenProps = {
  venues: VenueListItemResponseModel[]
}

export const IndividualOfferDetailsScreen = ({
  venues,
}: IndividualOfferDetailsScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const mode = useOfferWizardMode()

  const {
    categories,
    subCategories,
    offer: initialOffer,
    hasPublishedOfferWithSameEan,
  } = useIndividualOfferContext()
  const initialOfferImage = getIndividualOfferImage(initialOffer)
  const { handleEanImage } = useIndividualOfferImageUpload(initialOfferImage)

  const isNewOfferDraft = !initialOffer
  const availableVenues = filterAvailableVenues(venues)
  const availableVenuesAsOptions = getVenuesAsOptions(availableVenues)
  const isOfferArtistsFeatureActive = useActiveFeature('WIP_OFFER_ARTISTS')

  const getInitialValues = () => {
    return isNewOfferDraft
      ? getInitialValuesFromVenues(availableVenues, true)
      : getInitialValuesFromOffer({
          offer: initialOffer,
          subcategories: subCategories,
          isNewOfferCreationFlowFeatureActive: true,
        })
  }

  const form = useForm<DetailsFormValues>({
    defaultValues: getInitialValues(),
    resolver: yupResolver<DetailsFormValues, unknown, unknown>(
      getValidationSchema()
    ),
    mode: 'onBlur',
  })

  useEffect(() => {
    //  If we go from an offer edition details page to the offer creation,
    // the offerId is then null but the page remains the same so the form would not be reset
    form.reset(getInitialValues())
  }, [initialOffer?.id, form.reset])

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
    true
  )

  const onSubmit = async (formValues: DetailsFormValues): Promise<void> => {
    try {
      const initialOfferId = initialOffer?.id

      let offerId = initialOfferId

      if (isNewOfferDraft) {
        await mutate(
          [GET_OFFER_QUERY_KEY, offerId],
          api.postOffer(
            serializeDetailsPostData(formValues, isOfferArtistsFeatureActive)
          ),
          {
            revalidate: false,
            populateCache: (newOffer) => {
              offerId = newOffer.id
              return newOffer
            },
          }
        )
      } else if (initialOfferId) {
        await mutate(
          [GET_OFFER_QUERY_KEY, offerId],
          api.patchOffer(
            initialOfferId,
            serializeDetailsPatchData(formValues, isOfferArtistsFeatureActive)
          ),
          { revalidate: false }
        )
      }

      // replace url to fix back button
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
          offerId,
          mode,
          isOnboarding: pathname.indexOf('onboarding') !== -1,
        }),
        { replace: true }
      )
      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
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
      navigate(isOnboarding ? '/onboarding/individuel' : '/offre/creation')
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: initialOffer?.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
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
              filteredCategories={categories}
              filteredSubcategories={subCategories}
              hasSelectedProduct={hasSelectedProduct}
              isEanSearchDisplayed={isEanSearchInputDisplayed}
              readOnlyFields={readOnlyFields}
              venues={venues}
              venuesOptions={availableVenuesAsOptions}
            />
          </FormLayout>

          <ActionBar
            dirtyForm={form.formState.isDirty || isNewOfferDraft}
            isDisabled={
              form.formState.isSubmitting ||
              Boolean(initialOffer && isOfferDisabled(initialOffer)) ||
              hasPublishedOfferWithSameEan
            }
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION}
          />
        </form>
      </FormProvider>

      <RouteLeavingGuardIndividualOffer
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </>
  )
}
