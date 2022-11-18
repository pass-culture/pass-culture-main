import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { api } from 'apiClient/api'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import {
  getValidationSchema,
  buildInitialValues,
  IStockEventFormValues,
} from 'components/StockEventForm'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import { ActionBar } from '../ActionBar'

import { upsertStocksEventAdapter } from './adapters'
import { StockFormList } from './StockFormList'

export interface IStocksEventProps {
  offer: IOfferIndividual
}

const StocksEvent = ({ offer }: IStocksEventProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const [afterSubmitUrl, setAfterSubmitUrl] = useState<string>(
    getOfferIndividualUrl({
      offerId: offer.id,
      step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode,
    })
  )
  const navigate = useNavigate()
  const notify = useNotification()
  const { setOffer } = useOfferIndividualContext()

  const onSubmit = async (formValues: { stocks: IStockEventFormValues[] }) => {
    const { isOk, payload, message } = await upsertStocksEventAdapter({
      offerId: offer.id,
      formValues: formValues.stocks,
      departementCode: offer.venue.departmentCode,
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      notify.success(message)
      const response = await getOfferIndividualAdapter(offer.id)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      navigate(afterSubmitUrl)
    } else {
      /* istanbul ignore next: DEBT, TO FIX */
      formik.setErrors({ stocks: payload.errors })
    }
  }

  const onDeleteStock = async (stockValues: IStockEventFormValues) => {
    const { isDeletable, stockId } = stockValues
    stockId &&
      isDeletable &&
      api
        .deleteStock(stockId)
        .then(() => {
          notify.success('Le stock a été supprimé.')
        })
        .catch(() =>
          notify.error(
            'Une erreur est survenue lors de la suppression du stock.'
          )
        )
  }

  let minQuantity = null
  // validation is test in getValidationSchema
  // and it's not possible as is to test it here
  /* istanbul ignore next: DEBT, TO FIX */
  if (offer.stocks.length > 0) {
    minQuantity = offer.stocks[0].bookingsQuantity
  }
  const initialValues = buildInitialValues(offer)
  const { ...formik } = useFormik<{ stocks: IStockEventFormValues[] }>({
    initialValues,
    onSubmit,
    validationSchema: getValidationSchema(minQuantity),
  })

  const handleNextStep = () => {
    getOfferIndividualUrl({
      offerId: offer.id,
      step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode,
    })
    formik.handleSubmit()
  }

  const handlePreviousStep = () => {
    navigate(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      })
    )
  }

  const handleSaveDraft = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    if (!Object.keys(formik.touched).length)
      notify.success('Brouillon sauvegardé dans la liste des offres')
    else formik.handleSubmit()
    /* istanbul ignore next: DEBT, TO FIX */
    setAfterSubmitUrl(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      })
    )
  }

  return (
    <FormikProvider value={formik}>
      <FormLayout>
        <FormLayout.Section
          title="Stock & Prix"
          description={
            'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’événement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
          }
        >
          <form onSubmit={formik.handleSubmit}>
            <StockFormList offer={offer} onDeleteStock={onDeleteStock} />
            <ActionBar
              onClickNext={handleNextStep}
              onClickPrevious={handlePreviousStep}
              onClickSaveDraft={handleSaveDraft}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
            />
          </form>
        </FormLayout.Section>
      </FormLayout>
    </FormikProvider>
  )
}

export default StocksEvent
