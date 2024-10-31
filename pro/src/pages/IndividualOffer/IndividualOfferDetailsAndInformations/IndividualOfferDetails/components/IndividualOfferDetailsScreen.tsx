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
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import {
  isOfferProductBased,
  isOfferSynchronized,
} from 'commons/core/Offers/utils/typology'
import { PATCH_SUCCESS_MESSAGE } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import {
  isRecordStore,
  useSuggestedSubcategoriesAbTest,
} from 'commons/hooks/useSuggestedSubcategoriesAbTest'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import {
  getOfferSubtypeFromParam,
  getCategoryStatusFromOfferSubtype,
  filterCategories,
  isOfferSubtypeEvent,
} from 'pages/IndividualOffer/commons/filterCategories'
import { getFilteredVenueListByCategoryStatus } from 'pages/IndividualOffer/commons/getFilteredVenueList'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import {
  DetailsFormValues,
  Product,
} from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/commons/types'
import { useIndividualOfferImageUpload } from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/commons/useIndividualOfferImageUpload'
import {
  serializeDetailsPatchData,
  serializeDetailsPostData,
  setDefaultInitialValues,
  setDefaultInitialValuesFromOffer,
  setFormReadOnlyFields,
  hasMusicType,
} from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/commons/utils'
import { getValidationSchema } from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/commons/validationSchema'

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
  const { logEvent } = useAnalytics()
  const notify = useNotification()
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

  const isSearchByEanEnabled = useActiveFeature('WIP_EAN_CREATION')
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const { categories, subCategories, offer } = useIndividualOfferContext()
  const isDirtyDraftOffer = !offer

  const [filteredCategories, filteredSubcategories] = filterCategories(
    categories,
    subCategories,
    categoryStatus,
    isOfferSubtypeEvent(offerSubtype)
  )

  const filteredVenues = getFilteredVenueListByCategoryStatus(
    venues,
    categoryStatus
  )

  const areSuggestedSubcategoriesUsed =
    useSuggestedSubcategoriesAbTest(filteredVenues)

  const initialValues = isDirtyDraftOffer
    ? setDefaultInitialValues({
        filteredVenues,
        areSuggestedSubcategoriesUsed,
      })
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
        isOfferSynchronized(offer) ||
        (isSearchByEanEnabled && isOfferProductBased(offer))
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
        choosenSuggestedSubcategory: formik.values.suggestedSubcategory,
      })
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
      for (const field in error.body) {
        formik.setFieldError(field, error.body[field])
      }
      // This is used from scroll to error
      formik.setStatus('apiError')
    }

    if (offer && formik.dirty) {
      notify.success(PATCH_SUCCESS_MESSAGE)
    }
  }

  const formik = useFormik({
    initialValues,
    validationSchema: getValidationSchema({ isOfferAddressEnabled }),
    onSubmit,
  })
  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      navigate('/offre/creation')
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: offer?.id,
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
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

  const readOnlyFields = setFormReadOnlyFields(offer, isProductBased)
  const isEanSearchAvailable =
    isSearchByEanEnabled && isRecordStore(filteredVenues)
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
      suggestedSubcategory: '',
      productId: id.toString() || '',
    })
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
          resetForm={formik.resetForm}
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
              filteredVenues={filteredVenues}
              filteredCategories={filteredCategories}
              filteredSubcategories={filteredSubcategories}
              readonlyFields={readOnlyFields}
              onImageUpload={onImageUpload}
              onImageDelete={onImageDelete}
              imageOffer={imageOffer}
            />
          </FormLayout>
          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            onClickNext={async () => {
              if (
                areSuggestedSubcategoriesUsed &&
                formik.values.suggestedSubcategory === ''
              ) {
                await formik.setFieldValue('suggestedSubcategory', 'OTHER')
              }
            }}
            step={OFFER_WIZARD_STEP_IDS.DETAILS}
            isDisabled={
              formik.isSubmitting ||
              Boolean(offer && isOfferDisabled(offer.status))
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
