import { FormikProvider, useFormik } from 'formik'
import React, { useState, useEffect } from 'react'

import { api } from 'apiClient/api'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import {
  getValidationSchema,
  buildInitialValues,
  IStockEventFormValues,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from 'components/StockEventForm'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { useModal } from 'hooks/useModal'
import useNotification from 'hooks/useNotification'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar'
import DialogStocksEventEditConfirm from '../DialogStocksEventEditConfirm/DialogStocksEventEditConfirm'
import { useNotifyFormError } from '../hooks'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'
import { getSuccessMessage } from '../utils'
import { logTo } from '../utils/logTo'

import { upsertStocksEventAdapter } from './adapters'
import { StockFormList } from './StockFormList'

export interface IStocksEventProps {
  offer: IOfferIndividual
}

export const hasChangesOnStockWithBookings = (
  values: { stocks: IStockEventFormValues[] },
  initialValues: { stocks: IStockEventFormValues[] }
) => {
  const initialStocks: Record<
    string,
    Partial<IStockEventFormValues>
  > = initialValues.stocks.reduce(
    (dict: Record<string, Partial<IStockEventFormValues>>, stock) => {
      dict[stock.stockId || 'IStockEventFormValuesnewStock'] = {
        price: stock.price,
        beginningDate: stock.beginningDate,
        beginningTime: stock.beginningTime,
      }
      return dict
    },
    {}
  )

  return values.stocks.some(stock => {
    if (
      !stock.bookingsQuantity ||
      parseInt(stock.bookingsQuantity, 10) === 0 ||
      !stock.stockId
    ) {
      return false
    }
    const initialStock = initialStocks[stock.stockId]
    const fieldsWithWarning: (keyof IStockEventFormValues)[] = [
      'price',
      'beginningDate',
      'beginningTime',
    ]

    return fieldsWithWarning.some(
      (fieldName: keyof IStockEventFormValues) =>
        initialStock[fieldName] !== stock[fieldName]
    )
  })
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
  const [isSubmittingDraft, setIsSubmittingDraft] = useState<boolean>(false)
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const notify = useNotification()
  const { setOffer, shouldTrack, setShouldTrack } = useOfferIndividualContext()
  const providerName = offer?.lastProviderName
  const { visible, showModal, hideModal } = useModal()
  const isPriceCategoriesActive = useActiveFeature(
    'WIP_ENABLE_MULTI_PRICE_STOCKS'
  )
  const onSubmit = async (formValues: { stocks: IStockEventFormValues[] }) => {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      const changesOnStockWithBookings = hasChangesOnStockWithBookings(
        formValues,
        formik.initialValues
      )

      if (!visible && changesOnStockWithBookings) {
        showModal()
        return
      } else {
        hideModal()
      }
    }

    const { isOk, payload } = await upsertStocksEventAdapter({
      offerId: offer.id,
      formValues: formValues.stocks,
      departementCode: offer.venue.departmentCode,
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      notify.success(getSuccessMessage(mode))
      const response = await getOfferIndividualAdapter(offer.id)
      if (response.isOk) {
        const updatedOffer = response.payload
        setOffer && setOffer(updatedOffer)
        formik.resetForm({
          values: buildInitialValues({
            departmentCode: updatedOffer.venue.departmentCode,
            offerStocks: updatedOffer.stocks,
            today,
            lastProviderName: updatedOffer.lastProviderName,
            offerStatus: updatedOffer.status,
          }),
        })
      }
      if (!isSubmittingFromRouteLeavingGuard) {
        navigate(afterSubmitUrl)
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_WIZARD_STEP_IDS.STOCKS,
          to: isSubmittingDraft
            ? OFFER_WIZARD_STEP_IDS.STOCKS
            : OFFER_WIZARD_STEP_IDS.SUMMARY,
          used: isSubmittingDraft
            ? OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS
            : OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
          isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
          isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
          offerId: offer.id,
        })
      }
    } else {
      /* istanbul ignore next: DEBT, TO FIX */
      formik.setErrors({ stocks: payload.errors })
    }
    setIsClickingFromActionBar(false)
  }

  const onDeleteStock = async (
    stockValues: IStockEventFormValues,
    stockIndex: number
  ) => {
    const { isDeletable, stockId } = stockValues
    // tested but coverage don't see it.
    /* istanbul ignore next */
    if (stockId === undefined || !isDeletable) {
      return
    }
    try {
      await api.deleteStock(stockId)
      const response = await getOfferIndividualAdapter(offer.id)
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }

      const formStocks = [...formik.values.stocks]

      // When we delete a stock we must remove it from the initial values
      // otherwise it will trigger the routeLeavingGuard
      const initalStocks = [...formik.initialValues.stocks]
      initalStocks.splice(stockIndex, 1)
      formik.resetForm({
        values: { stocks: initalStocks },
      })

      // Set back possible user change.
      /* istanbul ignore next: DEBT, TO FIX */
      formStocks.splice(stockIndex, 1)
      /* istanbul ignore next: DEBT, TO FIX */
      formStocks.length
        ? formik.setValues({ stocks: formStocks })
        : formik.resetForm({
            values: { stocks: [STOCK_EVENT_FORM_DEFAULT_VALUES] },
          })
      notify.success('Le stock a été supprimé.')
    } catch {
      notify.error('Une erreur est survenue lors de la suppression du stock.')
    }
  }

  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departmentCode
  )
  const initialValues = buildInitialValues({
    departmentCode: offer.venue.departmentCode,
    offerStocks: offer.stocks,
    today,
    lastProviderName: offer.lastProviderName,
    offerStatus: offer.status,
  })

  const formik = useFormik<{ stocks: IStockEventFormValues[] }>({
    initialValues,
    onSubmit,
    validationSchema: getValidationSchema(),
  })

  const isFormEmpty = () => {
    return formik.values.stocks.every(
      val => val === STOCK_EVENT_FORM_DEFAULT_VALUES
    )
  }

  useNotifyFormError({
    isSubmitting: formik.isSubmitting,
    errors: formik.errors,
  })

  useEffect(() => {
    // when form is dirty it's tracked by RouteLeavingGuard
    setShouldTrack(!formik.dirty)
  }, [formik.dirty])

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)
      if (Object.keys(formik.errors).length !== 0) {
        /* istanbul ignore next: DEBT, TO FIX */
        setIsClickingFromActionBar(false)
      }

      // When saving draft with an empty form or in edition mode
      // we display a success notification even if nothing is done
      if (isFormEmpty() && (saveDraft || mode === OFFER_WIZARD_MODE.EDITION)) {
        setIsClickingFromActionBar(false)
        saveDraft
          ? notify.success('Brouillon sauvegardé dans la liste des offres')
          : notify.success(getSuccessMessage(mode))
        return
      }
      // tested but coverage don't see it.
      /* istanbul ignore next */
      setIsSubmittingDraft(saveDraft)
      setAfterSubmitUrl(
        getOfferIndividualUrl({
          offerId: offer.id,
          step: saveDraft
            ? OFFER_WIZARD_STEP_IDS.STOCKS
            : OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode,
        })
      )

      const hasSavedStock = formik.values.stocks.some(
        stock => stock.stockId !== undefined
      )

      /* istanbul ignore next: DEBT, TO FIX */
      if (hasSavedStock && !formik.dirty) {
        setIsClickingFromActionBar(false)
        /* istanbul ignore next: DEBT to fix */
        notify.success(getSuccessMessage(mode))
        /* istanbul ignore next: DEBT to fix */
        if (!saveDraft) {
          navigate(
            getOfferIndividualUrl({
              offerId: offer.id,
              step: saveDraft
                ? OFFER_WIZARD_STEP_IDS.STOCKS
                : OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode,
            })
          )
        }
        setIsClickingFromActionBar(false)
      } else {
        if (saveDraft) {
          await formik.submitForm()
        }
      }
    }

  useEffect(() => {
    if (!formik.isValid) {
      setIsClickingFromActionBar(false)
    }
  }, [formik.isValid])

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
        step: isPriceCategoriesActive
          ? OFFER_WIZARD_STEP_IDS.TARIFS
          : OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      })
    )
  }

  return (
    <FormikProvider value={formik}>
      {providerName && (
        <SynchronizedProviderInformation providerName={providerName} />
      )}
      {visible && (
        <DialogStocksEventEditConfirm
          onConfirm={formik.submitForm}
          onCancel={hideModal}
        />
      )}
      <FormLayout>
        <form onSubmit={formik.handleSubmit} data-testid="stock-event-form">
          <FormLayout.Section
            description={
              isOfferDisabled(offer.status)
                ? undefined
                : 'Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement. \n Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible.'
            }
            links={
              isOfferDisabled(offer.status)
                ? undefined
                : [
                    {
                      href: 'https://aide.passculture.app/hc/fr/articles/4411992053649--Acteurs-Culturels-Comment-annuler-ou-reporter-un-%C3%A9v%C3%A9nement-',
                      linkTitle: 'Comment reporter ou annuler un évènement ?',
                    },
                  ]
            }
            descriptionAsBanner={
              !isOfferDisabled(offer.status) &&
              mode === OFFER_WIZARD_MODE.EDITION
            }
          >
            <StockFormList offer={offer} onDeleteStock={onDeleteStock} />
            <ActionBar
              isDisabled={formik.isSubmitting || isOfferDisabled(offer.status)}
              onClickNext={handleNextStep()}
              onClickPrevious={handlePreviousStep}
              onClickSaveDraft={handleNextStep({ saveDraft: true })}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
              offerId={offer.id}
              shouldTrack={shouldTrack}
              isFormEmpty={isFormEmpty()}
            />
          </FormLayout.Section>
        </form>
      </FormLayout>

      <RouteLeavingGuardOfferIndividual
        when={formik.dirty && !isClickingFromActionBar}
        saveForm={formik.submitForm}
        setIsSubmittingFromRouteLeavingGuard={
          setIsSubmittingFromRouteLeavingGuard
        }
        mode={mode}
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
        hasOfferBeenCreated
      />
    </FormikProvider>
  )
}

export default StocksEvent
