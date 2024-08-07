import { Form, FormikProvider, useFormik } from 'formik'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { getFilteredVenueListByCategoryStatus } from 'components/IndividualOfferForm/utils/getFilteredVenueList'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { GET_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'

import { ActionBar } from '../ActionBar/ActionBar'
import { useIndividualOfferImageUpload } from '../hooks/useIndividualOfferImageUpload'
import {
  getOfferSubtypeFromParam,
  getCategoryStatusFromOfferSubtype,
  filterCategories,
  isOfferSubtypeEvent,
} from '../InformationsScreen/utils/filterCategories/filterCategories'

import { DetailsForm } from './DetailsForm'
import { DetailsFormValues } from './types'
import {
  serializeDetailsData,
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
  const notify = useNotification()
  const { mutate } = useSWRConfig()
  const { search } = useLocation()
  const mode = useOfferWizardMode()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useIndividualOfferImageUpload()
  const queryParams = new URLSearchParams(search)
  const queryOfferType = queryParams.get('offer-type')

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
  const initialValues =
    offer === null
      ? setDefaultInitialValues({ filteredVenues })
      : setDefaultInitialValuesFromOffer({
          offer,
          subcategories: subCategories,
        })

  const onSubmit = async (formValues: DetailsFormValues): Promise<void> => {
    // Submit
    try {
      const payload = serializeDetailsData(formValues)
      const response = !offer
        ? await api.postDraftOffer(payload)
        : await api.patchDraftOffer(offer.id, payload)

      const receivedOfferId = response.id
      await handleImageOnSubmit(receivedOfferId)
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

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
      // This is used from scroll to error
      formik.setStatus('apiError')
    }

    if (offer) {
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

  const readOnlyFields = setFormReadOnlyFields(offer)

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
          <ScrollToFirstErrorAfterSubmit />
          <FormLayout.MandatoryInfo />
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
