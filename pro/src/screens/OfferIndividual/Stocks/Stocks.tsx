import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useHistory } from 'react-router-dom'

import { IOfferIndividual } from 'core/Offers/types'
import { OfferFormLayout } from 'new_components/OfferFormLayout'

import { ActionBar } from '../ActionBar'

interface IStocksProps {
  offer: IOfferIndividual
}

const Stocks = ({ offer }: IStocksProps): JSX.Element => {
  const history = useHistory()
  const handleNextStep = () => {
    history.push(`/offre/${offer.id}/v3/creation/individuelle/recapitulatif`)
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

        <OfferFormLayout.ActionBar>
          <ActionBar
            onClickNext={handleNextStep}
            onClickPrevious={handlePreviousStep}
          />
        </OfferFormLayout.ActionBar>
      </form>
    </FormikProvider>
  )
}

export default Stocks
