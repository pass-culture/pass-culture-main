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
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'

import { ActionBar } from '../ActionBar/ActionBar'
import { serializeDurationMinutes } from '../InformationsScreen/serializePatchOffer'
import {
  getOfferSubtypeFromParam,
  getCategoryStatusFromOfferSubtype,
  filterCategories,
  isOfferSubtypeEvent,
} from '../InformationsScreen/utils/filterCategories/filterCategories'

import { DetailsForm } from './DetailsForm'
import { DetailsFormValues } from './types'
import {
  serializeExtraData,
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
      const postOffer = {
        description: formValues.description,
        durationMinutes: serializeDurationMinutes(
          formValues.durationMinutes ?? ''
        ),
        extraData: serializeExtraData(formValues),
        name: formValues.name,
        subcategoryId: formValues.subcategoryId,
        venueId: Number(formValues.venueId),
        // FIXME: remove these keys when the API is updated
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
      }

      const response = !offer
        ? await api.postOffer(postOffer)
        : await api.patchOffer(offer.id, postOffer)

      const receivedOfferId = response.id
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

      // replace url to fix back button
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
    const queryParams = new URLSearchParams(location.search)
    const queryOffererId = queryParams.get('structure')
    const queryVenueId = queryParams.get('lieu')
    /* istanbul ignore next: DEBT, TO FIX */
    navigate({
      pathname: '/offre/creation',
      search:
        queryOffererId && queryVenueId
          ? `lieu=${queryVenueId}&structure=${queryOffererId}`
          : queryOffererId && !queryVenueId
            ? `structure=${queryOffererId}`
            : '',
    })
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
