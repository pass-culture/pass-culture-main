import { yupResolver } from '@hookform/resolvers/yup'
import { format, isEqual } from 'date-fns'
import { ChangeEvent, useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, useLocation } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { FORMAT_ISO, getToday } from 'commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'commons/utils/timezone'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { FormLayoutDescription } from 'components/FormLayout/FormLayoutDescription'
import { StockFormRowAction } from 'components/IndividualOffer/StocksThing/StockThingFormActions/types'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import fullCodeIcon from 'icons/full-code.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { Checkbox } from 'ui-kit/formV2/Checkbox/Checkbox'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { QuantityInput } from 'ui-kit/formV2/QuantityInput/QuantityInput'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { DialogStockThingDeleteConfirm } from '../DialogStockDeleteConfirm/DialogStockThingDeleteConfirm'
import { useNotifyFormError } from '../hooks/useNotifyFormError'
import { getDepartmentCode } from '../utils/getDepartmentCode'
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
  offer: GetIndividualOfferWithAddressResponseModel
}

export const StocksThing = ({ offer }: StocksThingProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const notify = useNotification()
  const { subCategories, publishedOfferWithSameEAN } =
    useIndividualOfferContext()
  const { mutate } = useSWRConfig()
  const { logEvent } = useAnalytics()

  const [stocks, setStocks] = useState<GetOfferStockResponseModel[]>([])
  const [isActivationCodeFormVisible, setIsActivationCodeFormVisible] =
    useState(false)
  const [isDeleteConfirmVisible, setIsDeleteConfirmVisible] = useState(false)

  useEffect(() => {
    async function loadStocks() {
      const response = await api.getStocks(offer.id)
      setStocks(response.stocks)
      // Amine RESET avant la déclaration
      reset(buildInitialValues(offer, response.stocks))
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStocks()
  }, [])

  // validation is tested in getValidationSchema
  // and it's not possible as is to test it here
  /* istanbul ignore next: DEBT, TO FIX */
  const bookingsQuantity = stocks.length > 0 ? stocks[0].bookingsQuantity : 0
  const hasBookings = bookingsQuantity > 0
  const minQuantity =
    mode === OFFER_WIZARD_MODE.EDITION
      ? hasBookings
        ? bookingsQuantity
        : 0
      : 1
  const isDisabled = isOfferDisabled(offer.status)
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    getDepartmentCode(offer)
  )
  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const onSubmit = async (values: StockThingFormValues): Promise<void> => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
      isOnboarding,
    })

    // Return when saving in edition with an empty form
    const isFormEmpty = getValues() === STOCK_THING_FORM_DEFAULT_VALUES
    if (isFormEmpty && mode === OFFER_WIZARD_MODE.EDITION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Return when there is nothing to save
    const isStockAlreadySaved = watch('stockId') !== undefined
    if (isStockAlreadySaved && !isDirty) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Submit
    try {
      await submitToApi(values, offer, reset, setError)
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error.message)
      }
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offer.id])
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(nextStepUrl)
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(getSuccessMessage(mode))
    }
  }

  // TODO: for some reasons we cant use yup to make validation
  // happen or not - see conditions to support stock deletion.
  // No matter what, yup.when() always returns stockId as undefined
  // so this is a workaround to pass its value.
  const stockId = stocks.length > 0 ? stocks[0].id : undefined

  const hookForm = useForm({
    resolver: yupResolver(getValidationSchema(mode, bookingsQuantity, stockId)),
    defaultValues: buildInitialValues(offer, []),
    mode: 'onBlur',
  })

  const {
    register,
    setValue,
    getValues,
    handleSubmit,
    setError,
    reset,
    watch,
    formState: { errors, isSubmitting, isDirty, defaultValues },
  } = hookForm

  useNotifyFormError({
    isSubmitting: isSubmitting,
    errors,
  })

  console.log('err', errors)

  const handlePreviousStepOrBackToReadOnly = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode,
          isOnboarding,
        })
      )
    }
  }

  const onConfirmDeleteStock = async () => {
    if (watch('stockId') === undefined) {
      reset(STOCK_THING_FORM_DEFAULT_VALUES)
      return
    }
    try {
      await api.deleteStock(watch('stockId')!)
      await mutate([GET_OFFER_QUERY_KEY, offer.id])
      reset(STOCK_THING_FORM_DEFAULT_VALUES)
      setStocks([])
      notify.success('Le stock a été supprimé.')
    } catch {
      notify.error('Une erreur est survenue lors de la suppression du stock.')
    }
    setIsDeleteConfirmVisible(false)
  }

  const onQuantityChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const newQuantity = event.target.value
    if (newQuantity === '') {
      setValue('remainingQuantity', 'Illimité')
    } else {
      // No need to test
      /* istanbul ignore next */
      setValue(
        'remainingQuantity',
        (
          Number(newQuantity || 0) - Number(watch('bookingsQuantity') || 0)
        ).toString(10)
      )
    }
    setValue('quantity', parseInt(newQuantity), {
      shouldDirty: true,
      shouldValidate: true,
      shoudlTouch: true,
    })
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
          watch('stockId') !== undefined &&
          parseInt(watch('bookingsQuantity') ?? '0') > 0
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
    setValue('quantity', activationCodes.length)
    setValue('activationCodes', activationCodes)
    setIsActivationCodeFormVisible(false)
  }

  const readOnlyFields = publishedOfferWithSameEAN
    ? Object.keys(STOCK_THING_FORM_DEFAULT_VALUES)
    : setFormReadOnlyFields(offer, stocks, watch())
  const showExpirationDate = watch('activationCodesExpirationDatetime') != null

  const minExpirationDate = watch('bookingLimitDatetime') ?? null

  const maxDateTime = watch('activationCodesExpirationDatetime')

  return (
    <>
      <DialogStockThingDeleteConfirm
        onConfirm={onConfirmDeleteStock}
        onCancel={() => setIsDeleteConfirmVisible(false)}
        isDialogOpen={isDeleteConfirmVisible}
      />

      <ActivationCodeFormDialog
        onSubmit={submitActivationCodes}
        onCancel={() => setIsActivationCodeFormVisible(false)}
        today={today}
        minExpirationDate={minExpirationDate}
        isDialogOpen={isActivationCodeFormVisible}
      />

      <form onSubmit={handleSubmit(onSubmit)} data-testid="stock-thing-form">
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
                {...register('price')}
                /*smallLabel*/
                name="price"
                label="Prix"
                required
                /*classNameFooter={styles['field-layout-footer']}*/
                disabled={readOnlyFields.includes('price')}
                type="number"
                data-testid="input-price"
                rightIcon={strokeEuroIcon}
                step="0.01"
                min={0}
                className={styles['field-layout-xsmall']}
              />
              <DatePicker
                {...register('bookingLimitDatetime')}
                // TODO: amine smallLabel
                name="bookingLimitDatetime"
                label="Date limite de réservation"
                // TODO: amine hasLabelLineBreak={false}
                /*classNameFooter={styles['field-layout-footer']}*/
                minDate={today}
                maxDate={getMaximumBookingDatetime(maxDateTime)}
                disabled={readOnlyFields.includes('bookingLimitDatetime')}
                className={styles['field-layout-small']}
                onBlur={() => {
                  if (
                    defaultValues?.bookingLimitDatetime !==
                    watch('bookingLimitDatetime')
                  ) {
                    console.log(
                      'willo smith',
                      new Date(watch('bookingLimitDatetime')),
                      defaultValues?.bookingLimitDatetime,
                      defaultValues?.bookingLimitDatetime !==
                        new Date(watch('bookingLimitDatetime')),
                      !isEqual(
                        defaultValues?.bookingLimitDatetime,
                        new Date(watch('bookingLimitDatetime'))
                      )
                    )
                    logEvent(Events.UPDATED_BOOKING_LIMIT_DATE, {
                      from: location.pathname,
                      bookingLimitDatetime: format(
                        watch('bookingLimitDatetime') ?? new Date(),
                        FORMAT_ISO
                      ),
                    })
                  }
                }}
              />

              {showExpirationDate && (
                <DatePicker
                  value={watch('activationCodesExpirationDatetime')}
                  /*smallLabel*/
                  name="activationCodesExpirationDatetime"
                  label="Date d'expiration"
                  /*classNameFooter={styles['field-layout-footer']}*/
                  className={styles['field-layout-small']}
                  disabled={true}
                />
              )}
              <QuantityInput
                /*smallLabel*/
                value={watch('quantity') ?? undefined}
                label="Quantité"
                disabled={readOnlyFields.includes('quantity')}
                onChange={onQuantityChange}
                onBlur={onQuantityChange}
                className={styles['field-layout-small']}
                /*classNameFooter={styles['field-layout-footer']}*/
                minimum={minQuantity}
              />
              {mode === OFFER_WIZARD_MODE.EDITION && stocks.length > 0 && (
                <>
                  <TextInput
                    {...register('remainingQuantity')}
                    name="remainingQuantity"
                    readOnly
                    label="Stock restant"
                    hasLabelLineBreak={false}
                    isOptional
                    /*smallLabel*/
                    className={styles['field-layout-shrink']}
                    /*classNameFooter={styles['field-layout-footer']}*/
                  />
                  <TextInput
                    {...register('bookingsQuantity')}
                    name="bookingsQuantity"
                    value={watch('bookingsQuantity') || 0}
                    readOnly
                    label="Réservations"
                    isOptional
                    /*smallLabel*/
                    className={styles['field-layout-shrink']}
                    /*classNameFooter={styles['field-layout-footer']}*/
                  />
                </>
              )}
              {!publishedOfferWithSameEAN && actions.length > 0 && (
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
                  {...register('isDuo')}
                  label="Accepter les réservations “Duo“"
                  name="isDuo"
                  disabled={isDisabled}
                  variant={CheckboxVariant.BOX}
                />
              </FormLayout.Row>
            </FormLayout.Section>
          </FormLayout>
        )}
        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.STOCKS}
          isDisabled={
            isSubmitting || isDisabled || Boolean(publishedOfferWithSameEAN)
          }
          dirtyForm={isDirty}
        />
      </form>
      <RouteLeavingGuardIndividualOffer when={isDirty && !isSubmitting} />
    </>
  )
}
