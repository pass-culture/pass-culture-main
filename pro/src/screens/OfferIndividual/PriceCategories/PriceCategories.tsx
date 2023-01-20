/* istanbul ignore: DEBT, TO FIX */
import { FormikProvider, useFormik } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'

import { ActionBar } from '../ActionBar'

export interface IPriceCategories {
  offer: IOfferIndividual
}

const PriceCategories = ({ offer }: IPriceCategories): JSX.Element => {
  const navigate = useNavigate()
  const mode = useOfferWizardMode()

  const onSubmit = async (formValues: Record<string, any>) => {
    /* eslint-disable-next-line */
    console.log('submit !', formValues)
  }

  const formik = useFormik({
    initialValues: {},
    onSubmit,
  })

  const handlePreviousStep = () => {
    navigate(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      })
    )
  }

  return (
    <FormikProvider value={formik}>
      <FormLayout>
        <FormLayout.Section title="Tarifs">
          <form onSubmit={formik.handleSubmit}>
            <ActionBar
              onClickPrevious={handlePreviousStep}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
              isDisabled={formik.isSubmitting}
              offerId={offer.id}
            />
          </form>
        </FormLayout.Section>
      </FormLayout>
    </FormikProvider>
  )
}

export default PriceCategories
