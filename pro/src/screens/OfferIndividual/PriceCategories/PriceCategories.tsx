import { FormikProvider } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'

import { ActionBar } from '../ActionBar'

import { usePriceCategoriesForm } from './form/useForm'
import { PriceCategoriesForm } from './PriceCategoriesForm'

export interface IPriceCategories {
  offer: IOfferIndividual
}

const PriceCategories = ({ offer }: IPriceCategories): JSX.Element => {
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const formik = usePriceCategoriesForm()

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
        <form onSubmit={formik.handleSubmit}>
          <PriceCategoriesForm values={formik.values} />

          <ActionBar
            onClickPrevious={handlePreviousStep}
            step={OFFER_WIZARD_STEP_IDS.STOCKS}
            isDisabled={formik.isSubmitting}
            offerId={offer.id}
          />
        </form>
      </FormLayout>
    </FormikProvider>
  )
}

export default PriceCategories
