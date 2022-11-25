import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { api } from 'apiClient/api'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import {
  getValidationSchema,
  buildInitialValues,
  IStockEventFormValues,
} from 'components/StockEventForm'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'

import { ActionBar } from '../ActionBar'
import { logTo } from '../utils/logTo'

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
  const [
    isSubmittingFromRouteLeavingGuard,
    setIsSubmittingFromRouteLeavingGuard,
  ] = useState<boolean>(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const notify = useNotification()
  const { setOffer } = useOfferIndividualContext()

  const onSubmit = async (formValues: { stocks: IStockEventFormValues[] }) => {
    const { isOk, payload } = await upsertStocksEventAdapter({
      offerId: offer.id,
      formValues: formValues.stocks,
      departementCode: offer.venue.departmentCode,
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      notify.success(
        {
          [OFFER_WIZARD_MODE.CREATION]:
            'Brouillon sauvegardé dans la liste des offres',
          [OFFER_WIZARD_MODE.DRAFT]:
            'Brouillon sauvegardé dans la liste des offres',
          [OFFER_WIZARD_MODE.EDITION]:
            'Vos modifications ont bien été enregistrées',
        }[mode]
      )
      const response = await getOfferIndividualAdapter(offer.id)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      if (!isSubmittingFromRouteLeavingGuard) {
        navigate(afterSubmitUrl)
      }
    } else {
      /* istanbul ignore next: DEBT, TO FIX */
      formik.setErrors({ stocks: payload.errors })
    }
    setIsClickingFromActionBar(false)
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
  const formik = useFormik<{ stocks: IStockEventFormValues[] }>({
    initialValues,
    onSubmit,
    validationSchema: getValidationSchema(minQuantity),
    enableReinitialize: true,
  })

  const handleNextStep = () => {
    setIsClickingFromActionBar(true)
    setAfterSubmitUrl(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
      })
    )
    formik.handleSubmit()
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.STOCKS,
      to: OFFER_WIZARD_STEP_IDS.SUMMARY,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offer.id,
    })
  }

  const handlePreviousStep = () => {
    if (!formik.dirty) {
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.STOCKS,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: offer.id,
      })
    }
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      })
    )
  }

  const handleSaveDraft = () => {
    setIsClickingFromActionBar(true)
    /* istanbul ignore next: DEBT, TO FIX */
    setAfterSubmitUrl(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      })
    )
    /* istanbul ignore next: DEBT, TO FIX */
    if (!Object.keys(formik.touched).length) {
      notify.success('Brouillon sauvegardé dans la liste des offres')
    } else {
      formik.handleSubmit()
    }
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.STOCKS,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: true,
      offerId: offer.id,
    })
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
              isDisabled={formik.isSubmitting}
              onClickNext={handleNextStep}
              onClickPrevious={handlePreviousStep}
              onClickSaveDraft={handleSaveDraft}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
              offerId={offer.id}
            />
          </form>
        </FormLayout.Section>
      </FormLayout>
      {formik.dirty && !isClickingFromActionBar && (
        <RouteLeavingGuardOfferIndividual
          saveForm={formik.handleSubmit}
          setIsSubmittingFromRouteLeavingGuard={
            setIsSubmittingFromRouteLeavingGuard
          }
          mode={mode}
          hasOfferBeenCreated
          isFormValid={formik.isValid}
          tracking={nextLocation =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_WIZARD_STEP_IDS.STOCKS,
              to: logTo(nextLocation),
              used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
              isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
              isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
              offerId: offer?.id,
            })
          }
        />
      )}
    </FormikProvider>
  )
}

export default StocksEvent
