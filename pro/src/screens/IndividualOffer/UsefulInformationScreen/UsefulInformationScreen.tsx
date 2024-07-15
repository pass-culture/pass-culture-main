import { Form, FormikProvider, useFormik } from 'formik'
import { useNavigate } from 'react-router-dom'

import { VenueListItemResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'

import { ActionBar } from '../ActionBar/ActionBar'

import { DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES } from './constants'
import { UsefulInformationForm } from './UsefulInformationForm'

export type UsefulInformationScreenProps = {
  venues: VenueListItemResponseModel[]
}

export const UsefulInformationScreen = ({
  venues,
}: UsefulInformationScreenProps): JSX.Element => {
  const navigate = useNavigate()

  const formik = useFormik({
    initialValues: DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES,
    onSubmit: () => {},
  })
  const { offer } = useIndividualOfferContext()

  const handlePreviousStepOrBackToReadOnly = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getIndividualOfferUrl({
        offerId: offer?.id,
        step: OFFER_WIZARD_STEP_IDS.DETAILS,
        mode: OFFER_WIZARD_MODE.CREATION,
      })
    )
  }

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
          <FormLayout.MandatoryInfo />
          <UsefulInformationForm venues={venues} />
        </FormLayout>
        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.ABOUT}
          isDisabled={
            formik.isSubmitting ||
            Boolean(offer && isOfferDisabled(offer.status))
          }
          dirtyForm={formik.dirty}
        />
      </Form>
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}
