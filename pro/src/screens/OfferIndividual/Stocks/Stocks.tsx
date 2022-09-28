import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useHistory } from 'react-router-dom'

import { IOfferIndividual } from 'core/Offers/types'
import { OFFER_WIZARD_STEP_IDS } from 'new_components/OfferIndividualStepper'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'

import { ActionBar } from '../ActionBar'

interface IStocksProps {
  offer: IOfferIndividual
}

const Stocks = ({ offer }: IStocksProps): JSX.Element => {
  const history = useHistory()
  const isCreation = useIsCreation()
  const handleNextStep = () => {
    formik.handleSubmit()
    history.push(`/offre/${offer.id}/v3/creation/individuelle/recapitulatif`)
  }
  const handleSaveDraft = () => {
    formik.handleSubmit()
  }
  const handlePreviousStep = () => {
    history.push(`/offre/${offer.id}/v3/creation/individuelle/informations`)
  }

  const initialValues = {}
  const onSubmit = () => {
    // TODO stock submit
  }
  const validationSchema = {}

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  return (
    <FormikProvider value={{ ...formik, resetForm }}>
      <h2>Stock & Prix</h2>

      <form onSubmit={formik.handleSubmit}>
        <p> TODO stock form </p>

        <ActionBar
          onClickNext={handleNextStep}
          onClickSaveDraft={handleSaveDraft}
          onClickPrevious={handlePreviousStep}
          isCreation={isCreation}
          step={OFFER_WIZARD_STEP_IDS.STOCKS}
        />
      </form>
    </FormikProvider>
  )
}

export default Stocks
