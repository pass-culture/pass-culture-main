import cn from 'classnames'
import { FormikProvider, useFormik } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import FormLayout, { FormLayoutDescription } from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { StockFormActions } from 'components/StockFormActions'
import { IStockFormRowAction } from 'components/StockFormActions/types'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import {
  getOfferIndividualAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import {
  LIVRE_PAPIER_SUBCATEGORY_ID,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import { useModal } from 'hooks/useModal'
import useNotification from 'hooks/useNotification'
import { EuroIcon, TicketPlusFullIcon, TrashFilledIcon } from 'icons'
import { Checkbox, DatePicker, InfoBox, TextInput } from 'ui-kit'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar'
import { DialogStockThingDeleteConfirm } from '../DialogStockDeleteConfirm'
import { useNotifyFormError } from '../hooks'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'
import { getSuccessMessage } from '../utils'
import { logTo } from '../utils/logTo'

import { ActivationCodeFormDialog } from './ActivationCodeFormDialog'
import { upsertStocksThingAdapter } from './adapters'
import styles from './StockThing.module.scss'
import { setFormReadOnlyFields } from './utils'

import {
  buildInitialValues,
  getValidationSchema,
  IStockThingFormValues,
  STOCK_THING_FORM_DEFAULT_VALUES,
} from './'

export interface IStocksThingProps {
  offer: IOfferIndividual
}

const StocksThing = ({ offer }: IStocksThingProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const [afterSubmitUrl, setAfterSubmitUrl] = useState<string>(
    getOfferIndividualUrl({
      offerId: offer.nonHumanizedId,
      step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode,
    })
  )
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const [isSubmittingDraft, setIsSubmittingDraft] = useState<boolean>(false)
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const notify = useNotification()
  const { setOffer, shouldTrack, setShouldTrack, subCategories } =
    useOfferIndividualContext()

  const canBeDuo = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
  )?.canBeDuo

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
  const isDisabled = isOfferDisabled(offer.status)
  const providerName = offer?.lastProviderName

  const onSubmit = async (formValues: IStockThingFormValues) => {
    const serializedOffer = serializePatchOffer({
      offer: offer,
      formValues: { isDuo: formValues.isDuo },
    })
    const { isOk: isOfferOk, message: offerMessage } =
      await updateIndividualOffer({
        offerId: offer.nonHumanizedId,
        serializedOffer: serializedOffer,
      })
    if (!isOfferOk) {
      throw new Error(offerMessage)
    }

    const { isOk, payload, message } = await upsertStocksThingAdapter({
      offerId: offer.nonHumanizedId,
      formValues,
      departementCode: offer.venue.departmentCode,
      mode,
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      const response = await getOfferIndividualAdapter(offer.nonHumanizedId)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
        formik.resetForm({ values: buildInitialValues(response.payload) })
      }
      navigate(afterSubmitUrl)
      notify.success(message)
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
        offerId: offer.nonHumanizedId,
      })
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

      const nextStepUrl = getOfferIndividualUrl({
        offerId: offer.nonHumanizedId,
        step: saveDraft
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
      })

      // When saving draft with an empty form or in edition mode
      // we display a success notification even if nothing is done
      if (isFormEmpty() && (saveDraft || mode === OFFER_WIZARD_MODE.EDITION)) {
        setIsClickingFromActionBar(false)
        if (saveDraft) {
          notify.success('Brouillon sauvegardé dans la liste des offres')
          return
        } else {
          navigate(nextStepUrl)
          notify.success(getSuccessMessage(mode))
        }
      }
      // tested but coverage don't see it.
      /* istanbul ignore next */
      setIsSubmittingDraft(saveDraft)
      setAfterSubmitUrl(nextStepUrl)
      const hasSavedStock = formik.values.stockId !== undefined
      if (hasSavedStock && !formik.dirty) {
        if (!saveDraft) {
          navigate(nextStepUrl)
        }
        notify.success(getSuccessMessage(mode))
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
        offerId: offer.nonHumanizedId,
      })
    }
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getOfferIndividualUrl({
        offerId: offer.nonHumanizedId,
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
      const response = await getOfferIndividualAdapter(offer.nonHumanizedId)
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

  const onChangeQuantity = (event: React.ChangeEvent<HTMLInputElement>) => {
    const quantity = event.target.value
    let remainingQuantity: number | string =
      // No need to test
      /* istanbul ignore next */
      Number(quantity || 0) - Number(formik.values.bookingsQuantity || 0)

    if (quantity === '') {
      remainingQuantity = 'unlimited'
    }

    formik.setFieldValue(`remainingQuantity`, remainingQuantity)
    formik.setFieldValue(`quantity`, quantity)
  }

  const getMaximumBookingDatetime = (date: Date | undefined) => {
    if (date == undefined) {
      return undefined
    }
    const result = new Date(date)
    result.setDate(result.getDate() - 7)
    return result
  }

  const actions: IStockFormRowAction[] = [
    {
      callback: async () => {
        if (
          // tested but coverage don't see it.
          /* istanbul ignore next */
          mode === OFFER_WIZARD_MODE.EDITION &&
          formik.values.stockId !== undefined &&
          parseInt(formik.values.bookingsQuantity) > 0
        ) {
          deleteConfirmShow()
        } else {
          onConfirmDeleteStock()
        }
      },
      label: 'Supprimer le stock',
      disabled: false,
      Icon: TrashFilledIcon,
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
      Icon: TicketPlusFullIcon,
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

  const readOnlyFields = setFormReadOnlyFields(offer, formik.values)
  const showExpirationDate =
    formik.values.activationCodesExpirationDatetime !== null
  const maxDateTime =
    formik.values.activationCodesExpirationDatetime ?? undefined

  return (
    <FormikProvider value={formik}>
      {deleteConfirmVisible && (
        <DialogStockThingDeleteConfirm
          onConfirm={onConfirmDeleteStock}
          onCancel={deleteConfirmHide}
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
        <div aria-current="page">
          <FormLayoutDescription
            description={description}
            links={links}
            isBanner
          />
          <form onSubmit={formik.handleSubmit} data-testid="stock-thing-form">
            <div className={styles['stock-form-row']}>
              <div className={styles['stock-form']}>
                <TextInput
                  smallLabel
                  name="price"
                  label="Prix"
                  className={cn({
                    [styles['input-price']]: !showExpirationDate,
                  })}
                  classNameFooter={styles['field-layout-footer']}
                  disabled={readOnlyFields.includes('price')}
                  type="number"
                  data-testid="input-price"
                  rightIcon={() => <EuroIcon tabIndex={-1} />}
                  step="0.01"
                />
                <DatePicker
                  smallLabel
                  name="bookingLimitDatetime"
                  label="Date limite de réservation"
                  className={cn({
                    [styles['input-booking-limit-datetime']]:
                      !showExpirationDate,
                  })}
                  classNameFooter={styles['field-layout-footer']}
                  minDateTime={today}
                  maxDateTime={getMaximumBookingDatetime(maxDateTime)}
                  openingDateTime={today}
                  disabled={readOnlyFields.includes('bookingLimitDatetime')}
                />

                {showExpirationDate && (
                  <DatePicker
                    smallLabel
                    name="activationCodesExpirationDatetime"
                    label="Date d'expiration"
                    className={styles['input-activation-code']}
                    classNameFooter={styles['field-layout-footer']}
                    disabled={true}
                  />
                )}
                <TextInput
                  smallLabel
                  name="quantity"
                  label="Quantité"
                  placeholder="Illimité"
                  className={cn({
                    [styles['input-quantity']]: !showExpirationDate,
                  })}
                  classNameFooter={styles['field-layout-footer']}
                  disabled={readOnlyFields.includes('quantity')}
                  type="number"
                  hasDecimal={false}
                  onChange={onChangeQuantity}
                />
              </div>
              {mode === OFFER_WIZARD_MODE.EDITION &&
                offer.stocks.length > 0 && (
                  <div
                    className={cn(
                      styles['stock-form-info'],
                      styles['stock-form-info']
                    )}
                  >
                    <TextInput
                      name="availableStock"
                      value={
                        formik.values.remainingQuantity === 'unlimited'
                          ? 'Illimité'
                          : formik.values.remainingQuantity
                      }
                      readOnly
                      label="Stock restant"
                      smallLabel
                      classNameFooter={styles['field-layout-footer']}
                    />
                    <TextInput
                      name="bookingsQuantity"
                      value={formik.values.bookingsQuantity || 0}
                      readOnly
                      label="Réservations"
                      smallLabel
                      classNameFooter={styles['field-layout-footer']}
                    />
                  </div>
                )}

              {actions && actions.length > 0 && (
                <div className={styles['stock-actions']}>
                  <StockFormActions actions={actions} />
                </div>
              )}
            </div>

            <ActionBar
              onClickNext={handleNextStep()}
              onClickPrevious={handlePreviousStep}
              onClickSaveDraft={handleNextStep({ saveDraft: true })}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
              isDisabled={formik.isSubmitting || isDisabled}
              offerId={offer.nonHumanizedId}
              shouldTrack={shouldTrack}
              submitAsButton={isFormEmpty()}
            />
          </form>
        </div>
      </FormLayout>
      {canBeDuo && (
        <FormLayout small>
          <FormLayout.Section
            className={styles['duo-section']}
            title="Réservations “Duo”"
          >
            <FormLayout.Row
              sideComponent={
                <InfoBox>
                  Cette option permet au bénéficiaire de venir accompagné. La
                  seconde place sera délivrée au même tarif que la première,
                  quel que soit l'accompagnateur.
                </InfoBox>
              }
            >
              <Checkbox
                label="Accepter les réservations “Duo“"
                name="isDuo"
                disabled={isDisabled}
                withBorder
              />
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
      )}
      <RouteLeavingGuardOfferIndividual
        when={formik.dirty && !isClickingFromActionBar}
        tracking={nextLocation =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_WIZARD_STEP_IDS.STOCKS,
            to: logTo(nextLocation),
            used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
            isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
            isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
            offerId: offer?.nonHumanizedId,
          })
        }
      />
    </FormikProvider>
  )
}

export default StocksThing
