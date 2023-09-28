import cn from 'classnames'
import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import FormLayout, { FormLayoutDescription } from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer'
import { StockFormActions } from 'components/StockFormActions'
import { StockFormRowAction } from 'components/StockFormActions/types'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import {
  getIndividualOfferAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import {
  LIVRE_PAPIER_SUBCATEGORY_ID,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullCodeIcon from 'icons/full-code.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { Checkbox, DatePicker, InfoBox, TextInput } from 'ui-kit'
import { getToday, getYearMonthDay, isDateValid } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar'
import { DialogStockThingDeleteConfirm } from '../DialogStockDeleteConfirm'
import { useNotifyFormError } from '../hooks'
import { getSuccessMessage } from '../utils'
import { logTo } from '../utils/logTo'

import { ActivationCodeFormDialog } from './ActivationCodeFormDialog'
import { upsertStocksThingAdapter } from './adapters'
import styles from './StockThing.module.scss'
import { setFormReadOnlyFields } from './utils'

import {
  buildInitialValues,
  getValidationSchema,
  StockThingFormValues,
  STOCK_THING_FORM_DEFAULT_VALUES,
} from './'

export interface StocksThingProps {
  offer: IndividualOffer
}

const StocksThing = ({ offer }: StocksThingProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const [afterSubmitUrl, setAfterSubmitUrl] = useState<string>(
    getIndividualOfferUrl({
      offerId: offer.id,
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
    useIndividualOfferContext()

  const canBeDuo = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const [isActivationCodeFormVisible, setIsActivationCodeFormVisible] =
    useState(false)
  const [isDeleteConfirmVisible, setIsDeleteConfirmVisible] = useState(false)

  /* istanbul ignore next: DEBT, TO FIX */
  const isDisabled = isOfferDisabled(offer.status)

  const onSubmit = async (formValues: StockThingFormValues) => {
    const serializedOffer = serializePatchOffer({
      offer: offer,
      formValues: { isDuo: formValues.isDuo },
    })
    const { isOk: isOfferOk, message: offerMessage } =
      await updateIndividualOffer({
        offerId: offer.id,
        serializedOffer: serializedOffer,
      })
    if (!isOfferOk) {
      throw new Error(offerMessage)
    }

    const { isOk, payload, message } = await upsertStocksThingAdapter({
      offerId: offer.id,
      formValues,
      departementCode: offer.venue.departmentCode,
      mode,
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      const response = await getIndividualOfferAdapter(offer.id)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
        formik.resetForm({ values: buildInitialValues(response.payload) })
      }
      navigate(afterSubmitUrl)
      if (isSubmittingDraft || mode === OFFER_WIZARD_MODE.EDITION) {
        notify.success(message)
      }
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

      const nextStepUrl = getIndividualOfferUrl({
        offerId: offer.id,
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
          if (mode === OFFER_WIZARD_MODE.EDITION) {
            notify.success(getSuccessMessage(mode))
          }
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
        } else {
          notify.success(getSuccessMessage(mode))
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
      getIndividualOfferUrl({
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
      const response = await getIndividualOfferAdapter(offer.id)
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      formik.resetForm({ values: STOCK_THING_FORM_DEFAULT_VALUES })
      notify.success('Le stock a été supprimé.')
    } catch {
      notify.error('Une erreur est survenue lors de la suppression du stock.')
    }
    setIsDeleteConfirmVisible(false)
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

  const actions: StockFormRowAction[] = [
    {
      callback: async () => {
        if (
          // tested but coverage don't see it.
          /* istanbul ignore next */
          mode === OFFER_WIZARD_MODE.EDITION &&
          formik.values.stockId !== undefined &&
          parseInt(formik.values.bookingsQuantity) > 0
        ) {
          setIsDeleteConfirmVisible(true)
        } else {
          onConfirmDeleteStock()
        }
      },
      label: 'Supprimer le stock',
      disabled: false,
      icon: fullTrashIcon,
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
      callback: () => setIsActivationCodeFormVisible(true),
      label: "Ajouter des codes d'activation",
      disabled: isDisabled,
      icon: fullCodeIcon,
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

  const submitActivationCodes = (activationCodes: string[]) => {
    formik.setFieldValue('quantity', activationCodes?.length, true)
    formik.setFieldValue('activationCodes', activationCodes)
    setIsActivationCodeFormVisible(false)
  }

  const readOnlyFields = setFormReadOnlyFields(offer, formik.values)
  const showExpirationDate =
    formik.values.activationCodesExpirationDatetime !== ''

  const [minExpirationYear, minExpirationMonth, minExpirationDay] =
    getYearMonthDay(formik.values.bookingLimitDatetime)
  const [maxDateTimeYear, maxDateTimeMonth, maxDateTimeDay] = getYearMonthDay(
    formik.values.activationCodesExpirationDatetime
  )
  const minExpirationDate = isDateValid(formik.values.bookingLimitDatetime)
    ? new Date(minExpirationYear, minExpirationMonth, minExpirationDay)
    : null
  const maxDateTime = isDateValid(
    formik.values.activationCodesExpirationDatetime
  )
    ? new Date(maxDateTimeYear, maxDateTimeMonth, maxDateTimeDay)
    : undefined

  return (
    <FormikProvider value={formik}>
      {isDeleteConfirmVisible && (
        <DialogStockThingDeleteConfirm
          onConfirm={onConfirmDeleteStock}
          onCancel={() => setIsDeleteConfirmVisible(false)}
        />
      )}

      {isActivationCodeFormVisible && (
        <ActivationCodeFormDialog
          onSubmit={submitActivationCodes}
          onCancel={() => setIsActivationCodeFormVisible(false)}
          today={today}
          minExpirationDate={minExpirationDate}
        />
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
                  rightIcon={strokeEuroIcon}
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
                  minDate={today}
                  maxDate={getMaximumBookingDatetime(maxDateTime)}
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
              offerId={offer.id}
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
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !isClickingFromActionBar}
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
        isEdition={mode === OFFER_WIZARD_MODE.EDITION}
      />
    </FormikProvider>
  )
}

export default StocksThing
