import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { LIVRE_PAPIER_SUBCATEGORY_ID } from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { useNavigate } from 'hooks'
import useNotification from 'hooks/useNotification'
import FormLayout from 'new_components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'new_components/OfferIndividualStepper'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'
import { StockFormRow } from 'new_components/StockFormRow'
import {
  StockThingForm,
  getValidationSchema,
  buildInitialValues,
  IStockThingFormValues,
} from 'new_components/StockThingForm'
import setFormReadOnlyFields from 'new_components/StockThingForm/utils/setFormReadOnlyFields'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar'

import { upsertStocksThingAdapter } from './adapters'

export interface IStocksThingProps {
  offer: IOfferIndividual
}

const StocksThing = ({ offer }: IStocksThingProps): JSX.Element => {
  const isCreation = useIsCreation()
  const [afterSubmitUrl, setAfterSubmitUrl] = useState<string>(
    `/offre/${offer.id}/v3/creation/individuelle/recapitulatif`
  )
  const navigate = useNavigate()
  const notify = useNotification()
  const { setOffer } = useOfferIndividualContext()

  const onSubmit = async (formValues: IStockThingFormValues) => {
    const { isOk, payload, message } = await upsertStocksThingAdapter({
      offerId: offer.id,
      formValues,
      departementCode: offer.venue.departmentCode,
    })

    if (isOk) {
      notify.success(message)
      const response = await getOfferIndividualAdapter(offer.id)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      navigate(afterSubmitUrl)
    } else {
      formik.setErrors(payload.errors)
    }
  }

  let minQuantity = null
  // validation is test in getValidationSchema
  // and it's not possible as is to test it here
  /* istanbul ignore next: DEBT, TO FIX */
  if (offer.stocks.length > 0) {
    minQuantity = offer.stocks[0].bookingsQuantity
  }
  const today = getLocalDepartementDateTimeFromUtc(
    new Date(),
    offer.venue.departmentCode
  )
  const initialValues = buildInitialValues(offer)
  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema: getValidationSchema(minQuantity),
  })

  const handleNextStep = () => {
    setAfterSubmitUrl(
      `/offre/${offer.id}/v3/creation/individuelle/recapitulatif`
    )
    formik.handleSubmit()
  }

  const handlePreviousStep = () => {
    formik.handleSubmit()
    setAfterSubmitUrl(
      `/offre/${offer.id}/v3/creation/individuelle/informations`
    )
  }

  const renderStockForm = () => {
    return (
      <StockThingForm
        today={today}
        readOnlyFields={setFormReadOnlyFields(offer)}
      />
    )
  }

  let description
  if (offer.isDigital) {
    description = `Les utilisateurs ont ${
      offer.subcategoryId === LIVRE_PAPIER_SUBCATEGORY_ID ? '10' : '30'
    } jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.`
  } else {
    description =
      'Les utilisateurs ont 30 jours pour annuler leurs réservations d’offres numériques. Dans le cas d’offres avec codes d’activation, les utilisateurs ne peuvent pas annuler leurs réservations d’offres numériques. Toute réservation est définitive et sera immédiatement validée.'
  }

  return (
    <FormikProvider value={{ ...formik, resetForm }}>
      <FormLayout>
        <FormLayout.Section title="Stock & Prix" description={description}>
          <form onSubmit={formik.handleSubmit}>
            <StockFormRow
              Form={renderStockForm()}
              actions={[]}
              actionDisabled={false}
            />

            <ActionBar
              onClickNext={handleNextStep}
              onClickPrevious={handlePreviousStep}
              isCreation={isCreation}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
            />
          </form>
        </FormLayout.Section>
      </FormLayout>
    </FormikProvider>
  )
}

export default StocksThing
