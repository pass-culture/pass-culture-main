import { Form, FormikProvider, useFormik } from 'formik'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { VenueListItemResponseModel, VenueTypeCode } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { getFilteredVenueListByCategoryStatus } from 'components/IndividualOfferForm/utils/getFilteredVenueList'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { GET_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import { useSuggestedSubcategoriesAbTest } from 'hooks/useSuggestedSubcategoriesAbTest'

import { ActionBar } from '../ActionBar/ActionBar'
import { useIndividualOfferImageUpload } from '../hooks/useIndividualOfferImageUpload'
import {
  getOfferSubtypeFromParam,
  getCategoryStatusFromOfferSubtype,
  filterCategories,
  isOfferSubtypeEvent,
} from '../InformationsScreen/utils/filterCategories/filterCategories'

import { DetailsEanSearch } from './DetailsEanSearch/DetailsEanSearch'
import { DetailsForm } from './DetailsForm'
import { DetailsFormValues } from './types'
import {
  serializeDetailsPatchData,
  serializeDetailsPostData,
  setDefaultInitialValues,
  setDefaultInitialValuesFromOffer,
  setFormReadOnlyFields,
} from './utils'
import { validationSchema } from './validationSchema'

export type DetailsScreenProps = {
  venues: VenueListItemResponseModel[]
}

export const DetailsScreen = ({ venues }: DetailsScreenProps): JSX.Element => {
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

  const areSuggestedSubcategoriesUsed = useSuggestedSubcategoriesAbTest()
  const isSearchByEanEnabled = useActiveFeature('WIP_EAN_CREATION')

  const { categories, subCategories, offer } = useIndividualOfferContext()
  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  const categoryStatus = getCategoryStatusFromOfferSubtype(offerSubtype)

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
  const isRecordStore = filteredVenues.some(
    (venue) => venue.venueTypeCode === ('RECORD_STORE' as VenueTypeCode)
  )

  const initialValues =
    offer === null
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
      const isProviderOffer = !!offer?.lastProvider
      const shouldNotPatchData =
        isProviderOffer || (!isSearchByEanEnabled && !!offer?.productId)
      let receivedOfferId = offer?.id
      let response
      if (!offer) {
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
    validationSchema,
    onSubmit,
  })

  const handlePreviousStepOrBackToReadOnly = () => {
    mode === OFFER_WIZARD_MODE.CREATION
      ? navigate('/offre/creation')
      : navigate(
          getIndividualOfferUrl({
            offerId: offer?.id,
            step: OFFER_WIZARD_STEP_IDS.DETAILS,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })
        )
  }

  // (Draft) offers are created via POST request.
  // On Details screen, the form might be pre-filled with a product,
  // until the form is submitted, the draft offer is not created yet.
  const isOfferProductBased = !!offer?.productId
  const isNotAnOfferYetButProductBased = !offer && !!formik.values.productId
  const isProductBased = isOfferProductBased || isNotAnOfferYetButProductBased

  const readOnlyFields = setFormReadOnlyFields(offer, isProductBased)
  const shouldDisplayEanSearch =
    isSearchByEanEnabled && isRecordStore && mode === OFFER_WIZARD_MODE.CREATION

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
          <ScrollToFirstErrorAfterSubmit />
          <FormLayout.MandatoryInfo />
          {shouldDisplayEanSearch && (
            <DetailsEanSearch
              setImageOffer={setImageOffer}
              isOfferProductBased={isOfferProductBased}
            />
          )}
          <DetailsForm
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
  )
}
