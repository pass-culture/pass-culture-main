import { FormikProvider, useFormik } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { IStockFormRowAction } from 'components/StockFormActions/types'
import {
  StockThingForm,
  getValidationSchema,
  buildInitialValues,
  IStockThingFormValues,
  STOCK_THING_FORM_DEFAULT_VALUES,
} from 'components/StockThingForm'
import { setFormReadOnlyFields } from 'components/StockThingForm/utils'
import { StockThingFormRow } from 'components/StockThingFormRow'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import {
  LIVRE_PAPIER_SUBCATEGORY_ID,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import { useModal } from 'hooks/useModal'
import useNotification from 'hooks/useNotification'
import { IcoTicketPlusFull, IcoTrashFilled } from 'icons'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar'
import { DialogStockDeleteConfirm } from '../DialogStockDeleteConfirm'
import { useNotifyFormError } from '../hooks'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'
import { getSuccessMessage } from '../utils'
import { logTo } from '../utils/logTo'

import { ActivationCodeFormDialog } from './ActivationCodeFormDialog'
import { upsertStocksThingAdapter } from './adapters'

export interface IStocksThingProps {
  offer: IOfferIndividual
}

const StocksThing = ({ offer }: IStocksThingProps): JSX.Element => {
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
  const {
    visible: activationCodeFormVisible,
    showModal: activationCodeFormShow,
    hideModal: activationCodeFormHide,
  } = useModal()
  const {
    visible: deleteConfirmVisible,
    showModal: deleteConfirmShow,
    hideModal: deleteConfirmHide,
  } = useModal()
  /* istanbul ignore next: DEBT, TO FIX */
  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const providerName = offer?.lastProviderName

  const onSubmit = async (formValues: IStockThingFormValues) => {
    const { isOk, payload, message } = await upsertStocksThingAdapter({
      offerId: offer.id,
      formValues,
      departementCode: offer.venue.departmentCode,
      mode,
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      notify.success(message)
      const response = await getOfferIndividualAdapter(offer.id)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
        formik.resetForm({ values: buildInitialValues(response.payload) })
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
      formik.setErrors(payload.errors)
    }
    setIsClickingFromActionBar(false)
  }

  let minQuantity = null
  // validation is test in getValidationSchema
  // and it's not possible as is to test it here
  /* istanbul ignore next: DEBT, TO FIX */
  if (offer.stocks.length > 0) {
    minQuantity = offer.stocks[0].bookingsQuantity
  }
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departmentCode
  )
  const initialValues = buildInitialValues(offer)
  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema: getValidationSchema(minQuantity),
  })

  useEffect(() => {
    // when form is dirty it's tracked by RouteLeavingGuard
    setShouldTrack(!formik.dirty)
  }, [formik.dirty])

  const isFormEmpty = () => {
    return formik.values === STOCK_THING_FORM_DEFAULT_VALUES
  }

  useNotifyFormError({
    isSubmitting: formik.isSubmitting,
    errors: formik.errors,
  })

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)
      /* istanbul ignore next: DEBT, TO FIX */
      if (Object.keys(formik.errors).length !== 0) {
        setIsClickingFromActionBar(false)
      }

      // When saving draft with an empty form
      // we display a success notification even if nothing is done
      if (saveDraft && isFormEmpty()) {
        setIsClickingFromActionBar(false)
        notify.success('Brouillon sauvegardé dans la liste des offres')
        return
      }
      // tested but coverage don't see it.
      /* istanbul ignore next */
      setIsSubmittingDraft(saveDraft)
      const nextStepUrl = getOfferIndividualUrl({
        offerId: offer.id,
        step: saveDraft
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
      })
      setAfterSubmitUrl(nextStepUrl)

      const hasSavedStock = formik.values.stockId !== undefined
      if (hasSavedStock && !formik.dirty) {
        notify.success(getSuccessMessage(mode))
        if (!saveDraft) {
          navigate(nextStepUrl)
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
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      })
    )
  }

  const onConfirmDeleteStock = async () => {
    /* istanbul ignore next: DEBT, TO FIX */
    if (formik.values.stockId === undefined) {
      formik.resetForm({ values: STOCK_THING_FORM_DEFAULT_VALUES })
      return
    }
    try {
      await api.deleteStock(formik.values.stockId)
      const response = await getOfferIndividualAdapter(offer.id)
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      formik.resetForm({ values: STOCK_THING_FORM_DEFAULT_VALUES })
      notify.success('Le stock a été supprimé.')
    } catch {
      notify.error('Une erreur est survenue lors de la suppression du stock.')
    }
    deleteConfirmHide()
  }

  const actions: IStockFormRowAction[] = [
    {
      callback:
        /* istanbul ignore next: DEBT, TO FIX */
        formik.values.bookingsQuantity !== '0'
          ? deleteConfirmShow
          : onConfirmDeleteStock,
      label: 'Supprimer le stock',
      disabled: false,
      Icon: IcoTrashFilled,
    },
  ]

  let description
  let links
  if (!offer.isDigital) {
    description = `Les bénéficiaires ont ${
      offer.subcategoryId === LIVRE_PAPIER_SUBCATEGORY_ID ? '10' : '30'
    } jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.`
  } else {
    description = `Les bénéficiaires ont 30 jours pour annuler leurs réservations d’offres numériques.

    Dans le cas d’offres avec codes d’activation, les bénéficiaires ne peuvent pas annuler leurs réservations. Toute réservation est définitive et sera immédiatement validée.`

    let isDisabled = false
    if (offer.stocks.length > 0 && offer.stocks[0].hasActivationCode) {
      isDisabled = true
    }

    actions.push({
      callback: activationCodeFormShow,
      label: "Ajouter des codes d'activation",
      disabled: isDisabled,
      Icon: IcoTicketPlusFull,
    })
  }

  actions[0].disabled = isDisabled

  if (offer.isDigital) {
    description += `
    Pour ajouter des codes d’activation, veuillez passer par le menu ··· et choisir l’option correspondante.`

    links = [
      {
        href: 'https://aide.passculture.app/hc/fr/articles/4411991970705--Acteurs-culturels-Comment-cr%C3%A9er-une-offre-num%C3%A9rique-avec-des-codes-d-activation-',
        linkTitle: 'Comment gérer les codes d’activation ?',
      },
    ]
  }

  const submitActivationCodes = useCallback(
    (activationCodes: string[]) => {
      formik.setFieldValue('quantity', activationCodes?.length, true)
      formik.setFieldValue('activationCodes', activationCodes)
      activationCodeFormHide()
    },
    [activationCodeFormHide]
  )

  return (
    <FormikProvider value={formik}>
      {deleteConfirmVisible && (
        <DialogStockDeleteConfirm
          onConfirm={onConfirmDeleteStock}
          onCancel={deleteConfirmHide}
          isEvent={true}
        />
      )}
      {activationCodeFormVisible && (
        <ActivationCodeFormDialog
          onSubmit={submitActivationCodes}
          onCancel={activationCodeFormHide}
          today={today}
          minExpirationDate={formik.values.bookingLimitDatetime}
        />
      )}

      {providerName && (
        <SynchronizedProviderInformation providerName={providerName} />
      )}
      <FormLayout>
        <FormLayout.Section
          title="Stock & Prix"
          description={description}
          links={links}
          descriptionAsBanner={mode === OFFER_WIZARD_MODE.EDITION}
        >
          <form onSubmit={formik.handleSubmit}>
            <StockThingFormRow
              actions={actions}
              actionDisabled={false}
              showStockInfo={
                mode === OFFER_WIZARD_MODE.EDITION && offer.stocks.length > 0
              }
            >
              <StockThingForm
                today={today}
                readOnlyFields={setFormReadOnlyFields(offer, formik.values)}
                showExpirationDate={
                  formik.values.activationCodesExpirationDatetime !== null
                }
              />
            </StockThingFormRow>

            <ActionBar
              onClickNext={handleNextStep()}
              onClickPrevious={handlePreviousStep}
              onClickSaveDraft={handleNextStep({ saveDraft: true })}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
              isDisabled={formik.isSubmitting}
              offerId={offer.id}
              shouldTrack={shouldTrack}
            />
          </form>
        </FormLayout.Section>
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

export default StocksThing
