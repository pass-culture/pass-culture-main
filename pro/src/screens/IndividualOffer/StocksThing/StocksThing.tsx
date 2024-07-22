import { FormikProvider, useFormik } from 'formik'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { FormLayoutDescription } from 'components/FormLayout/FormLayoutDescription'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { GET_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useNotification } from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import fullCodeIcon from 'icons/full-code.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { StockFormRowAction } from 'screens/IndividualOffer/StocksThing/StockThingFormActions/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { getToday, getYearMonthDay, isDateValid } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar/ActionBar'
import { DialogStockThingDeleteConfirm } from '../DialogStockDeleteConfirm/DialogStockThingDeleteConfirm'
import { useNotifyFormError } from '../hooks/useNotifyFormError'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { ActivationCodeFormDialog } from './ActivationCodeFormDialog/ActivationCodeFormDialog'
import { STOCK_THING_FORM_DEFAULT_VALUES } from './constants'
import styles from './StockThing.module.scss'
import { StockThingFormActions } from './StockThingFormActions/StockThingFormActions'
import { submitToApi } from './submitToApi'
import { StockThingFormValues } from './types'
import { buildInitialValues } from './utils/buildInitialValues'
import { setFormReadOnlyFields } from './utils/setFormReadOnlyFields'
import { getValidationSchema } from './validationSchema'

export interface StocksThingProps {
  offer: GetIndividualOfferResponseModel
}

export const StocksThing = ({ offer }: StocksThingProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const notify = useNotification()
  const { subCategories } = useIndividualOfferContext()
  const { mutate } = useSWRConfig()

  const [stocks, setStocks] = useState<GetOfferStockResponseModel[]>([])
  const [isActivationCodeFormVisible, setIsActivationCodeFormVisible] =
    useState(false)
  const [isDeleteConfirmVisible, setIsDeleteConfirmVisible] = useState(false)

  useEffect(() => {
    async function loadStocks() {
      const response = await api.getStocks(offer.id)
      setStocks(response.stocks)
      formik.resetForm({ values: buildInitialValues(offer, response.stocks) })
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStocks()
  }, [])

  // validation is tested in getValidationSchema
  // and it's not possible as is to test it here
  /* istanbul ignore next: DEBT, TO FIX */
  const minQuantity = stocks.length > 0 ? stocks[0].bookingsQuantity : null
  const isDisabled = isOfferDisabled(offer.status)
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departementCode
  )
  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const onSubmit = async (values: StockThingFormValues) => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
    })

    // Return when saving in edition with an empty form
    const isFormEmpty = formik.values === STOCK_THING_FORM_DEFAULT_VALUES
    if (isFormEmpty && mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Return when there is nothing to save
    const isStockAlreadySaved = formik.values.stockId !== undefined
    if (isStockAlreadySaved && !formik.dirty) {
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Submit
    try {
      await submitToApi(values, offer, formik.resetForm, formik.setErrors)
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error.message)
      }
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offer.id])
    navigate(nextStepUrl)
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(getSuccessMessage(mode))
    }
  }

  const formik = useFormik({
    initialValues: buildInitialValues(offer, []),
    onSubmit,
    validationSchema: getValidationSchema(mode, minQuantity),
  })

  useNotifyFormError({
    isSubmitting: formik.isSubmitting,
    errors: formik.errors,
  })

  const handlePreviousStepOrBackToReadOnly = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    mode === OFFER_WIZARD_MODE.EDITION
      ? navigate(
          getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })
        )
      : navigate(
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
      await mutate([GET_OFFER_QUERY_KEY, offer.id])
      formik.resetForm({ values: STOCK_THING_FORM_DEFAULT_VALUES })
      notify.success('Le stock a été supprimé.')
    } catch {
      notify.error('Une erreur est survenue lors de la suppression du stock.')
    }
    setIsDeleteConfirmVisible(false)
  }

  const onChangeQuantity = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const quantity = event.target.value
    let remainingQuantity: number | string =
      // No need to test
      /* istanbul ignore next */
      Number(quantity || 0) - Number(formik.values.bookingsQuantity || 0)

    if (quantity === '') {
      remainingQuantity = 'unlimited'
    }

    await formik.setFieldValue(`remainingQuantity`, remainingQuantity)
    await formik.setFieldValue(`quantity`, quantity)
  }

  const getMaximumBookingDatetime = (date: Date | undefined) => {
    if (date === undefined) {
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
          await onConfirmDeleteStock()
        }
      },
      label: 'Supprimer le stock',
      disabled: false,
      icon: fullTrashIcon,
    },
  ]

  let description: string | JSX.Element
  let links
  if (!offer.isDigital) {
    description = `Les bénéficiaires ont ${
      offer.subcategoryId === SubcategoryIdEnum.LIVRE_PAPIER ? '10' : '30'
    } jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.`
  } else {
    description = (
      <div>
        <p className={styles['callout-area']}>
          <strong>
            Les bénéficiaires ont 30 jours pour annuler leurs réservations
            d’offres numériques.
          </strong>
        </p>
        <p>
          Dans le cas d’offres avec codes d’activation, les bénéficiaires ne
          peuvent pas annuler leurs réservations. Toute réservation est
          définitive et sera immédiatement validée.
        </p>
        <p>
          Pour ajouter des codes d’activation, veuillez passer par le menu et
          choisir l’option correspondante.
        </p>
      </div>
    )

    let isDisabled = false
    if (stocks.length > 0 && stocks[0].hasActivationCode) {
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
    links = [
      {
        href: 'https://aide.passculture.app/hc/fr/articles/4411991970705--Acteurs-culturels-Comment-cr%C3%A9er-une-offre-num%C3%A9rique-avec-des-codes-d-activation',
        label: 'Comment gérer les codes d’activation ?',
        isExternal: true,
      },
    ]
  }

  const submitActivationCodes = async (activationCodes: string[]) => {
    await formik.setFieldValue('quantity', activationCodes.length, true)
    await formik.setFieldValue('activationCodes', activationCodes)
    setIsActivationCodeFormVisible(false)
  }

  const readOnlyFields = setFormReadOnlyFields(offer, stocks, formik.values)
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

      <form onSubmit={formik.handleSubmit} data-testid="stock-thing-form">
        <FormLayout>
          <div aria-current="page">
            <div className={styles['mandatory']}>
              Tous les champs suivis d’un * sont obligatoires.
            </div>
            <FormLayoutDescription
              description={description}
              links={links}
              isBanner
              className={styles['callout-area-margin']}
            />

            <div className={styles['row']}>
              <TextInput
                smallLabel
                name="price"
                label="Prix"
                classNameFooter={styles['field-layout-footer']}
                disabled={readOnlyFields.includes('price')}
                type="number"
                data-testid="input-price"
                rightIcon={strokeEuroIcon}
                step="0.01"
                className={styles['field-layout-xsmall']}
              />
              <DatePicker
                smallLabel
                name="bookingLimitDatetime"
                label="Date limite de réservation"
                isOptional
                hasLabelLineBreak={false}
                classNameFooter={styles['field-layout-footer']}
                minDate={today}
                maxDate={getMaximumBookingDatetime(maxDateTime)}
                disabled={readOnlyFields.includes('bookingLimitDatetime')}
                className={styles['field-layout-small']}
              />

              {showExpirationDate && (
                <DatePicker
                  smallLabel
                  name="activationCodesExpirationDatetime"
                  label="Date d'expiration"
                  classNameFooter={styles['field-layout-footer']}
                  disabled={true}
                  className={styles['field-layout-small']}
                />
              )}
              <TextInput
                smallLabel
                name="quantity"
                label="Quantité"
                placeholder="Illimité"
                isOptional
                classNameFooter={styles['field-layout-footer']}
                disabled={readOnlyFields.includes('quantity')}
                type="number"
                hasDecimal={false}
                onChange={onChangeQuantity}
                className={styles['field-layout-xsmall']}
              />
              {mode === OFFER_WIZARD_MODE.EDITION && stocks.length > 0 && (
                <>
                  <TextInput
                    name="availableStock"
                    value={
                      formik.values.remainingQuantity === 'unlimited'
                        ? 'Illimité'
                        : formik.values.remainingQuantity
                    }
                    readOnly
                    label="Stock restant"
                    hasLabelLineBreak={false}
                    isOptional
                    smallLabel
                    className={styles['field-layout-shrink']}
                    classNameFooter={styles['field-layout-footer']}
                  />
                  <TextInput
                    name="bookingsQuantity"
                    value={formik.values.bookingsQuantity || 0}
                    readOnly
                    label="Réservations"
                    isOptional
                    smallLabel
                    className={styles['field-layout-shrink']}
                    classNameFooter={styles['field-layout-footer']}
                  />
                </>
              )}

              {actions.length > 0 && (
                <StockThingFormActions actions={actions} />
              )}
            </div>
          </div>
        </FormLayout>

        {canBeDuo && (
          <FormLayout fullWidthActions>
            <FormLayout.Section
              className={styles['duo-section']}
              title="Réservations “Duo”"
            >
              <FormLayout.Row
                sideComponent={
                  <InfoBox>
                    Cette option permet au bénéficiaire de venir accompagné. La
                    seconde place sera délivrée au même tarif que la première,
                    quel que soit l’accompagnateur.
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
        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.STOCKS}
          isDisabled={formik.isSubmitting || isDisabled}
          dirtyForm={formik.dirty}
        />
      </form>
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}
