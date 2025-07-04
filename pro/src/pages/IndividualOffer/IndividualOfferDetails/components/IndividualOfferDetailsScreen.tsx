import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  GetIndividualOfferResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { isOfferSynchronized } from 'commons/core/Offers/utils/typology'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { getIndividualOfferImage } from 'components/IndividualOffer/utils/getIndividualOfferImage'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import {
  filterCategories,
  getCategoryStatusFromOfferSubtype,
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from 'pages/IndividualOffer/commons/filterCategories'
import { isRecordStore } from 'pages/IndividualOffer/commons/isRecordStore'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import {
  DetailsFormValues,
  Product,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { useIndividualOfferImageUpload } from 'pages/IndividualOffer/IndividualOfferDetails/commons/useIndividualOfferImageUpload'
import {
  formatVenuesOptions,
  hasMusicType,
  serializeDetailsPatchData,
  serializeDetailsPostData,
  setDefaultInitialValuesFromOffer,
  setFormReadOnlyFields,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { getValidationSchema } from 'pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'

import { DEFAULT_DETAILS_FORM_VALUES } from '../commons/constants'

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
  const { search } = useLocation()
  const mode = useOfferWizardMode()
  const queryParams = new URLSearchParams(search)
  const queryOfferType = queryParams.get('offer-type')
  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  const categoryStatus = getCategoryStatusFromOfferSubtype(offerSubtype)

  const { categories, subCategories, offer, publishedOfferWithSameEAN } =
    useIndividualOfferContext()
  const initialImageOffer = getIndividualOfferImage(offer)
  const {
    displayedImage,
    hasUpsertedImage,
    onImageDelete,
    onImageUpload,
    handleEanImage,
    handleImageOnSubmit,
  } = useIndividualOfferImageUpload(initialImageOffer)
  const isDraftOffer = !offer

  const [filteredCategories, filteredSubcategories] = filterCategories(
    categories,
    subCategories,
    categoryStatus,
    isOfferSubtypeEvent(offerSubtype)
  )

  const availableVenuesOptions = formatVenuesOptions(
    venues,
    categoryStatus === CATEGORY_STATUS.ONLINE || Boolean(offer?.isDigital)
  )

  const initialValues = isDraftOffer
    ? //  When there is only one venue available the venueId field is not displayed
      //  Thus we need to set the venueId programmatically
      {
        ...DEFAULT_DETAILS_FORM_VALUES,
        venueId:
          availableVenuesOptions.length === 1
            ? availableVenuesOptions[0]?.value
            : '',
      }
    : setDefaultInitialValuesFromOffer({
        offer,
        subcategories: subCategories,
      })

  const form = useForm<DetailsFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver<DetailsFormValues>(
      getValidationSchema({
        isDigitalOffer:
          categoryStatus === CATEGORY_STATUS.ONLINE ||
          Boolean(offer?.isDigital),
      })
    ),
    mode: 'onBlur',
  })

  // Either draft or already created product-based offer.
  const isProductBased = !!form.watch('productId')
  const isOfferProductBased = !isDraftOffer && isProductBased

  const onSubmit = async (formValues: DetailsFormValues): Promise<void> => {
    try {
      // Draft offer PATCH requests are useless for product-based offers
      // and synchronized / provider offers since neither of the inputs displayed in
      // DetailsScreen can be edited at all
      const shouldNotPatchData =
        isOfferSynchronized(offer) || isOfferProductBased
      const initialOfferId = offer?.id

      let response: GetIndividualOfferResponseModel | undefined
      let offerId = initialOfferId

      if (isDraftOffer) {
        response = await api.postDraftOffer(
          serializeDetailsPostData(formValues)
        )
      } else if (!shouldNotPatchData && initialOfferId) {
        response = await api.patchDraftOffer(
          initialOfferId,
          serializeDetailsPatchData(formValues)
        )
      }

      offerId = response?.id ?? initialOfferId

      // Images can never be uploaded for product-based offers,
      // the drag & drop should not be displayed / enabled so
      // this is a safeguard.
      if (!!offerId && !isProductBased) {
        await handleImageOnSubmit(offerId)
        await mutate([GET_OFFER_QUERY_KEY, offerId])
      }

      // replace url to fix back button
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          offerId,
          mode,
          isOnboarding: pathname.indexOf('onboarding') !== -1,
        }),
        { replace: true }
      )
      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.DETAILS
          : OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.DETAILS,
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
          offerId: offer?.id,
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
    }
  }

  const readOnlyFields = setFormReadOnlyFields(offer, isProductBased)

  const isEanSearchAvailable =
    isRecordStore(venues) &&
    queryOfferType === INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
  const isEanSearchDisplayed =
    isEanSearchAvailable &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    (isDraftOffer || isProductBased)
  const isEanSearchCalloutAloneDisplayed =
    isEanSearchAvailable &&
    mode === OFFER_WIZARD_MODE.EDITION &&
    isOfferProductBased

  const onEanSearch = (ean: string, product: Product) => {
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

    const { categoryId, conditionalFields: subcategoryConditionalFields } =
      subCategory

    const imageUrl = images.recto
    if (imageUrl) {
      handleEanImage(imageUrl)
    }

    let gtl_id = ''
    if (hasMusicType(categoryId, subcategoryConditionalFields)) {
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
      subcategoryConditionalFields as (keyof DetailsFormValues)[]
    )
    form.setValue('productId', id.toString() || '')
  }

  const onEanReset = () => {
    handleEanImage()
    form.reset()
  }

  return (
    <>
      <FormLayout.MandatoryInfo />
      {isEanSearchDisplayed && (
        <DetailsEanSearch
          isDraftOffer={isDraftOffer}
          isProductBased={isProductBased}
          subcategoryId={form.watch('subcategoryId')}
          initialEan={offer?.extraData?.ean}
          onEanSearch={onEanSearch}
          onEanReset={onEanReset}
        />
      )}
      {isEanSearchCalloutAloneDisplayed && (
        <EanSearchCallout isDraftOffer={false} />
      )}
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FormLayout fullWidthActions>
            <ScrollToFirstHookFormErrorAfterSubmit />
            <DetailsForm
              isEanSearchDisplayed={isEanSearchDisplayed}
              isProductBased={isProductBased}
              filteredCategories={filteredCategories}
              filteredSubcategories={filteredSubcategories}
              readOnlyFields={readOnlyFields}
              venuesOptions={availableVenuesOptions}
              categoryStatus={categoryStatus}
              displayedImage={displayedImage}
              onImageUpload={onImageUpload}
              onImageDelete={onImageDelete}
            />
          </FormLayout>
          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={OFFER_WIZARD_STEP_IDS.DETAILS}
            isDisabled={
              form.formState.isSubmitting ||
              Boolean(offer && isOfferDisabled(offer.status)) ||
              Boolean(publishedOfferWithSameEAN)
            }
            dirtyForm={form.formState.isDirty || offer === null}
          />
        </form>
        <RouteLeavingGuardIndividualOffer
          when={
            (form.formState.isDirty || hasUpsertedImage) &&
            !form.formState.isSubmitting
          }
        />
      </FormProvider>
    </>
  )
}
