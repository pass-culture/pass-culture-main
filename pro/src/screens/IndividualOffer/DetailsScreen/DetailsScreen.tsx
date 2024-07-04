import { Form, FormikProvider, useFormik } from 'formik'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { DetailsForm } from './DetailsForm'
import { DEFAULT_DETAILS_INTITIAL_VALUES } from './constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { ActionBar } from '../ActionBar/ActionBar'
import { useNavigate } from 'react-router-dom'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { VenueListItemResponseModel } from 'apiClient/v1'

type DetailsScreenProps = {
  venues: VenueListItemResponseModel[]
}

export const DetailsScreen = ({ venues }: DetailsScreenProps): JSX.Element => {
  const navigate = useNavigate()

  const formik = useFormik({
    initialValues: DEFAULT_DETAILS_INTITIAL_VALUES,
    onSubmit: () => {},
  })
  const { offer } = useIndividualOfferContext()

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

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
          <FormLayout.MandatoryInfo />
          <DetailsForm venues={venues} />
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
