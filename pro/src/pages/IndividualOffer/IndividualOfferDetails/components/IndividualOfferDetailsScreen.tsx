import { Form, FormikProvider, useFormik } from 'formik'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { VenueListItemResponseModel } from 'apiClient/v1'
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
import {
  isOfferProductBased,
  isOfferSynchronized,
} from 'commons/core/Offers/utils/typology'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
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
  const {
    imageOffer,
    setImageOffer,
    onImageDelete,
    onImageUpload,
    handleImageOnSubmit,
  } = useIndividualOfferImageUpload()
  const queryParams = new URLSearchParams(search)
  const queryOfferType = queryParams.get('offer-type')
  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  const categoryStatus = getCategoryStatusFromOfferSubtype(offerSubtype)

  const { categories, subCategories, offer, publishedOfferWithSameEAN } =
    useIndividualOfferContext()
  const isDirtyDraftOffer = !offer

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

  const initialValues = isDirtyDraftOffer
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

  const onSubmit = async (formValues: DetailsFormValues): Promise<void> => {
    // Submit
    try {
      // Draft offer PATCH requests are useless for product-based offers
      // and synchronized / provider offers since neither of the inputs displayed in
      // DetailsScreen can be edited at all
      const shouldNotPatchData =
        isOfferSynchronized(offer) || isOfferProductBased(offer)
      let receivedOfferId = offer?.id
      let response
      if (isDirtyDraftOffer) {
        response = await api.postDraftOffer(
          serializeDetailsPostData(formValues)
        )
      } else if (!shouldNotPatchData) {
        // Draft offer PATCH requests are useless for product-based offers and synchronized / provider offers since neither of the inputs displayed in DetailsScreen can be edited at all
        response = await api.patchDraftOffer(
          offer.id,
          serializeDetailsPatchData(formValues)
        )
      }

      if (response) {
        receivedOfferId = response.id
        await handleImageOnSubmit(receivedOfferId)
        await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])
      }

      // replace url to fix back button
      navigate(
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          offerId: receivedOfferId,
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
        offerId: receivedOfferId,
        venueId: formik.values.venueId,
        offerType: 'individual',
        subcategoryId: formik.values.subcategoryId,
      })
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
        formik.setFieldError(field, error.body[field])
      }
      // This is used from scroll to error
      formik.setStatus('apiError')
    }
  }
  const formik = useFormik({
    initialValues,
    validationSchema: getValidationSchema({
      isDigitalOffer:
        categoryStatus === CATEGORY_STATUS.ONLINE || Boolean(offer?.isDigital),
    }),
    onSubmit,
  })
  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      navigate(`${isOnboarding ? '/onboarding' : ''}/offre/creation`)
    } else {
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

  // (Draft) offers are created via POST request.
  // On Details screen, the form might be pre-filled with a product,
  // until the form is submitted, the draft offer is not created yet.
  const isOfferButNotProductBased =
    !isDirtyDraftOffer && !isOfferProductBased(offer)
  const isProductBased = !!formik.values.productId

  const readOnlyFields = publishedOfferWithSameEAN
    ? Object.keys(DEFAULT_DETAILS_FORM_VALUES)
    : setFormReadOnlyFields(offer, isProductBased)
  const isEanSearchAvailable =
    isRecordStore(venues) &&
    queryOfferType === INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
  const isEanSearchDisplayed =
    isEanSearchAvailable &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    !isOfferButNotProductBased
  const isEanSearchCalloutAloneDisplayed =
    isEanSearchAvailable &&
    mode === OFFER_WIZARD_MODE.EDITION &&
    isOfferProductBased(offer)

  const onEanSearch = async (ean: string, product: Product): Promise<void> => {
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
      setImageOffer({
        originalUrl: imageUrl,
        url: imageUrl,
        credit: null,
      })
    }

    let gtl_id = ''
    if (hasMusicType(categoryId, subcategoryConditionalFields)) {
      // Fallback to "Autre" in case of missing gtlId
      // to define "Genre musical" when relevant.
      gtl_id = gtlId || '19000000'
    }

    await formik.setValues({
      ...formik.values,
      ean,
      name,
      description: description || '',
      categoryId,
      subcategoryId,
      gtl_id,
      author,
      performer,
      subcategoryConditionalFields,
      productId: id.toString() || '',
    })
  }

  const onEanReset = () => {
    setImageOffer(undefined)
    formik.resetForm()
  }

  return (
    <>
      <FormLayout.MandatoryInfo />
      {isEanSearchDisplayed && (
        <DetailsEanSearch
          isDirtyDraftOffer={isDirtyDraftOffer}
          productId={formik.values.productId}
          subcategoryId={formik.values.subcategoryId}
          initialEan={offer?.extraData?.ean}
          eanSubmitError={formik.status === 'apiError' ? formik.errors.ean : ''}
          onEanSearch={onEanSearch}
          onEanReset={onEanReset}
        />
      )}
      {isEanSearchCalloutAloneDisplayed && <EanSearchCallout />}
      <FormikProvider value={formik}>
        <Form>
          <FormLayout fullWidthActions>
            <ScrollToFirstErrorAfterSubmit />
            <DetailsForm
              isEanSearchDisplayed={isEanSearchDisplayed}
              isProductBased={isProductBased}
              filteredCategories={filteredCategories}
              filteredSubcategories={filteredSubcategories}
              readOnlyFields={readOnlyFields}
              onImageUpload={onImageUpload}
              onImageDelete={onImageDelete}
              imageOffer={imageOffer}
              venuesOptions={availableVenuesOptions}
              categoryStatus={categoryStatus}
            />
          </FormLayout>
          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={OFFER_WIZARD_STEP_IDS.DETAILS}
            isDisabled={
              formik.isSubmitting ||
              Boolean(offer && isOfferDisabled(offer.status)) ||
              Boolean(publishedOfferWithSameEAN)
            }
            dirtyForm={formik.dirty || offer === null}
          />
        </Form>
        <RouteLeavingGuardIndividualOffer
          when={formik.dirty && !formik.isSubmitting}
        />
      </FormikProvider>
    </>
  )
}
