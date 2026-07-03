import { yupResolver } from '@hookform/resolvers/yup'
import cn from 'classnames'
import { FormProvider, useForm } from 'react-hook-form'

import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  type CollectiveStockCreationBodyModel,
  type CollectiveStockResponseModel,
} from '@/apiClient/v1'
import { Mode } from '@/commons/core/OfferEducational/types'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isDateValid } from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeCollaborator from '@/icons/stroke-collaborator.svg'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'

import { AdditionalFeesForm } from '../AdditionalFeesForm/AdditionalFeesForm'
import { buildDatetimesForStock } from '../utils/buildDatetimesForStock'
import { computePriceForStock } from '../utils/computePriceForStock'
import { MAX_PRICE } from '../utils/constants'
import { extractFormDates } from '../utils/extractFormDates'
import styles from './CollectiveOfferStockForm.module.scss'
import {
  type CollectiveOfferStockFormValues,
  generateValidationSchema,
} from './validationSchema'

export interface CollectiveOfferStockFormProps {
  initialStock: Partial<CollectiveStockResponseModel>
  departementCode: string
  allowedActions: CollectiveOfferAllowedAction[]
  onSubmit: (
    newCollectiveStock: Partial<CollectiveStockCreationBodyModel>
  ) => Promise<void>
  mode: Mode
  goBackLink?: string
}

export const CollectiveOfferStockForm = ({
  initialStock,
  departementCode,
  allowedActions,
  onSubmit,
  mode,
  goBackLink = '/offres/collectives',
}: CollectiveOfferStockFormProps): JSX.Element => {
  const snackBar = useSnackBar()
  const canEditDiscount = allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
  )

  const canEditDates = allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DATES
  )

  const canEditDetails = allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DATES
  )

  const {
    startDatetime,
    endDatetime,
    bookingLimitDatetime,
    numberOfTickets,
    numberOfTeachers,
    servicePrice,
    collectiveAdditionalFees,
    price: initialPrice,
  } = initialStock

  const initialDatesValues = extractFormDates(
    { startDatetime, endDatetime, bookingLimitDatetime },
    departementCode
  )

  const form = useForm<CollectiveOfferStockFormValues>({
    defaultValues: {
      numberOfTickets,
      numberOfTeachers,
      servicePrice: servicePrice ?? undefined,
      hasAdditionalFees: Boolean(
        collectiveAdditionalFees && collectiveAdditionalFees.length > 0
      ),
      collectiveAdditionalFees: collectiveAdditionalFees || [],
      ...initialDatesValues,
    },
    resolver: yupResolver(
      generateValidationSchema(
        canEditDetails,
        canEditDates,
        canEditDiscount,
        initialPrice
      )
    ),
    mode: 'onSubmit',
  })

  const servicePriceValue = form.watch('servicePrice')
  const additionalFeesValue = form.watch('collectiveAdditionalFees')
  const price = computePriceForStock(servicePriceValue, additionalFeesValue)
  const isPriceTooHigh = price > MAX_PRICE

  const postForm = async (formValues: CollectiveOfferStockFormValues) => {
    try {
      const {
        numberOfTickets,
        numberOfTeachers,
        servicePrice,
        hasAdditionalFees,
        collectiveAdditionalFees,
        ...dateFormValues
      } = formValues

      const updatedStock: Partial<CollectiveStockCreationBodyModel> = {}
      const dirtyKeys = new Set(Object.keys(form.formState.dirtyFields))
      const shouldSaveAllFields = !initialStock.id

      if (shouldSaveAllFields || dirtyKeys.has('numberOfTickets')) {
        updatedStock.numberOfTickets = numberOfTickets
      }
      if (shouldSaveAllFields || dirtyKeys.has('numberOfTeachers')) {
        updatedStock.numberOfTeachers = numberOfTeachers
      }

      const hasDirtyPrice =
        dirtyKeys.has('servicePrice') ||
        dirtyKeys.has('hasAdditionalFees') ||
        dirtyKeys.has('collectiveAdditionalFees')
      if (shouldSaveAllFields || hasDirtyPrice) {
        updatedStock.servicePrice = servicePrice
        updatedStock.collectiveAdditionalFees = hasAdditionalFees
          ? collectiveAdditionalFees
          : []
        updatedStock.price = price
      }

      const hasDirtyDates = Object.keys(dateFormValues).some((k) =>
        dirtyKeys.has(k)
      )
      if (shouldSaveAllFields || hasDirtyDates) {
        const stockDates = buildDatetimesForStock(
          dateFormValues,
          departementCode
        )
        Object.assign(updatedStock, stockDates)
      }
      await onSubmit(updatedStock)
    } catch (error) {
      if (isErrorAPIError(error) && error.status < 500) {
        if ('price' in error.body) {
          error.body.servicePrice = error.body.price
          error.body['collectiveAdditionalFees.root'] = error.body.price
          delete error.body.price
        }
        if ('global' in error.body) {
          snackBar.error(error.body.global.join(' '))
        }
        serializeApiErrors(error.body, form.setError)
      } else {
        snackBar.error(
          "Une erreur est survenue lors de l'enregistrement de votre stock."
        )
      }
    }
  }

  const endDateValue = form.watch('endDate')
  const startDateValue = form.watch('startDate')

  function handleStartDateChange(event: React.ChangeEvent<HTMLInputElement>) {
    form.setValue('startDate', event.target.value, {
      shouldValidate: true,
      shouldDirty: true,
      shouldTouch: true,
    })
    if (!isDateValid(endDateValue) || endDateValue < event.target.value) {
      form.setValue('endDate', event.target.value, {
        shouldValidate: true,
        shouldDirty: true,
      })
    }
  }

  const minEndDate = isDateValid(startDateValue)
    ? new Date(startDateValue)
    : new Date()

  return (
    <FormProvider {...form}>
      <form noValidate onSubmit={form.handleSubmit(postForm)}>
        <ScrollToFirstHookFormErrorAfterSubmit />

        <FormLayout className={styles['collective-offer-stock-form-layout']}>
          <FormLayout.MandatoryInfo />
          <div className={styles['collective-offer-stock-banner']}>
            <Banner
              title="Modification autorisée"
              actions={[
                {
                  href: 'https://passculture.zendesk.com/hc/fr/articles/4412973958673--Acteurs-culturels-Comment-modifier-une-offre-collective-pr%C3%A9-r%C3%A9serv%C3%A9e-',
                  label:
                    'Consultez l’article “Comment modifier ou annuler une offre collective pré-réservée”',
                  isExternal: true,
                  type: 'link',
                  icon: fullLinkIcon,
                  iconAlt: 'Nouvelle fenêtre',
                },
              ]}
              description="Ces informations peuvent être modifiées jusqu'à validation de la réservation par le chef d'établissement."
            />
          </div>
          <FormLayout.Section
            title="Date de votre offre"
            description="Le remboursement de votre offre sera effectué 2 à 3 semaines après la date de fin de votre événement."
          >
            <FormLayout.Row inline>
              <DatePicker
                {...form.register('startDate')}
                disabled={!canEditDates}
                error={form.formState.errors.startDate?.message}
                label={'Date de début'}
                minDate={new Date()}
                onChange={handleStartDateChange}
                required
              />
              <DatePicker
                {...form.register('endDate')}
                disabled={!canEditDates}
                error={form.formState.errors.endDate?.message}
                label={'Date de fin'}
                minDate={minEndDate}
                required
              />
              <TimePicker
                {...form.register('eventTime')}
                disabled={!canEditDates}
                error={form.formState.errors.eventTime?.message}
                label={'Horaire de début'}
                required
              />
            </FormLayout.Row>
          </FormLayout.Section>
          <FormLayout.Section
            title="Date limite de réservation"
            description="Indiquez la date limite avant laquelle l’offre doit être réservée par l’enseignant puis par le chef d’établissement. À défaut, l’offre expirera et ne sera plus visible sur ADAGE."
          >
            <FormLayout.Row inline>
              <DatePicker
                {...form.register('bookingLimitDate')}
                disabled={!canEditDates}
                error={form.formState.errors.bookingLimitDate?.message}
                label={'Date limite de réservation'}
                maxDate={
                  isDateValid(new Date(startDateValue))
                    ? new Date(startDateValue)
                    : undefined
                }
                minDate={new Date()}
                required
              />
            </FormLayout.Row>
          </FormLayout.Section>
          <FormLayout.Section title="Nombre de participants">
            <FormLayout.Row inline>
              <TextInput
                {...form.register('numberOfTickets', { valueAsNumber: true })}
                disabled={!canEditDiscount}
                error={form.formState.errors.numberOfTickets?.message}
                icon={strokeCollaborator}
                label={"Nombre d'élèves"}
                required
                type="number"
              />
              <TextInput
                {...form.register('numberOfTeachers', { valueAsNumber: true })}
                disabled={!canEditDiscount}
                error={form.formState.errors.numberOfTeachers?.message}
                icon={strokeCollaborator}
                label={"Nombre d'accompagnateurs"}
                required
                type="number"
              />
            </FormLayout.Row>
          </FormLayout.Section>
          <FormLayout.Section title="Prix de votre offre">
            <FormLayout.SubSection
              title="Tarif de la prestation"
              description="Le tarif de la prestation doit être indiqué hors frais annexes et toutes charges comprises."
            >
              <FormLayout.Row inline>
                <TextInput
                  {...form.register('servicePrice', {
                    valueAsNumber: true,
                    onChange: () =>
                      form.trigger([
                        'collectiveAdditionalFees',
                        'servicePrice',
                      ]),
                  })}
                  disabled={!canEditDiscount}
                  error={form.formState.errors.servicePrice?.message}
                  label="Tarif de la prestation (en €)"
                  min={0}
                  required
                  step={0.01}
                  type="number"
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
            <FormLayout.SubSection title="Frais annexes">
              <AdditionalFeesForm canEditDiscount={canEditDiscount} />
            </FormLayout.SubSection>
          </FormLayout.Section>
          <FormLayout.Section
            title={
              <>
                Prix total de votre offre :{' '}
                <span
                  className={cn(styles['collective-offer-stock-price'], {
                    [styles['error']]: isPriceTooHigh,
                  })}
                >
                  {formatPrice(price)} TTC
                </span>
              </>
            }
            description="Le prix total de votre offre est calculé en fonction du tarif de la prestation et des potentiels frais annexes indiqués."
          >
            <div></div>
          </FormLayout.Section>
          <ActionsBarSticky>
            <ActionsBarSticky.Left>
              <Button
                as="a"
                color={
                  mode === Mode.CREATION
                    ? ButtonColor.BRAND
                    : ButtonColor.NEUTRAL
                }
                label={mode === Mode.CREATION ? 'Retour' : 'Annuler et quitter'}
                to={goBackLink}
                variant={ButtonVariant.SECONDARY}
              />
            </ActionsBarSticky.Left>

            <ActionsBarSticky.Right
              dirtyForm={form.formState.isDirty}
              mode={mode}
            >
              <Button
                disabled={!(canEditDiscount || canEditDates)}
                isLoading={form.formState.isSubmitting}
                label="Enregistrer et continuer"
                type="submit"
              />
            </ActionsBarSticky.Right>
          </ActionsBarSticky>
        </FormLayout>
      </form>
      <RouteLeavingGuardCollectiveOfferCreation
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </FormProvider>
  )
}
