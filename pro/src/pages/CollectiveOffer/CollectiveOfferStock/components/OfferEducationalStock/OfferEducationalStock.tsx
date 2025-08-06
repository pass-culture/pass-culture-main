/* @debt standard "Gautier: Do not load internal page dependencies"*/

import { yupResolver } from '@hookform/resolvers/yup'
import { addDays, isBefore } from 'date-fns'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import {
  CollectiveBookingStatus,
  CollectiveOfferAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import {
  isCollectiveOffer,
  Mode,
  OfferEducationalStockFormValues,
} from '@/commons/core/OfferEducational/types'
import { NBSP } from '@/commons/core/shared/constants'
import { isDateValid } from '@/commons/utils/date'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from '@/components/BannerPublicApi/BannerPublicApi'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OfferEducationalActions } from '@/components/OfferEducationalActions/OfferEducationalActions'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  DETAILS_PRICE_LABEL,
  PRICE_DETAIL_PLACEHOLDER,
} from './constants/labels'
import { FormStock } from './FormStock/FormStock'
import styles from './OfferEducationalStock.module.scss'
import { generateValidationSchema } from './validationSchema'

export interface OfferEducationalStockProps<
  T = GetCollectiveOfferResponseModel | GetCollectiveOfferTemplateResponseModel,
> {
  initialValues: OfferEducationalStockFormValues
  offer: T
  onSubmit: (offer: T, values: OfferEducationalStockFormValues) => Promise<void>
  mode: Mode
  requestId?: string | null
}

export const OfferEducationalStock = <
  T extends
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel,
>({
  initialValues,
  offer,
  onSubmit,
  mode,
  requestId = '',
}: OfferEducationalStockProps<T>): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const startDatetime =
    isCollectiveOffer(offer) && offer.collectiveStock?.startDatetime

  const preventPriceIncrease = Boolean(
    isCollectiveOffer(offer) &&
      (offer.booking?.status === CollectiveBookingStatus.CONFIRMED ||
        (offer.booking?.status === CollectiveBookingStatus.USED &&
          startDatetime &&
          isBefore(new Date(), addDays(new Date(startDatetime), 2))))
  )

  const canEditDiscount = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
  )

  const canEditDates = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_EDIT_DATES
  )

  const postForm = async (values: OfferEducationalStockFormValues) => {
    setIsLoading(true)
    await onSubmit(offer, values)
    setIsLoading(false)
  }

  const form = useForm({
    defaultValues: initialValues,
    resolver: yupResolver<OfferEducationalStockFormValues>(
      generateValidationSchema(
        preventPriceIncrease,
        initialValues.totalPrice,
        mode === Mode.READ_ONLY
      )
    ),
    mode: 'onSubmit',
  })

  const values = form.watch()

  return (
    <>
      <OfferEducationalActions
        className={styles.actions}
        offer={offer}
        mode={mode}
      />
      <FormProvider {...form}>
        <form noValidate onSubmit={form.handleSubmit(postForm)}>
          <ScrollToFirstHookFormErrorAfterSubmit />

          <FormLayout className={styles['offer-educational-stock-form-layout']}>
            {isCollectiveOffer(offer) && offer.isPublicApi && (
              <BannerPublicApi className={styles['banner-space']}>
                Offre importée automatiquement
              </BannerPublicApi>
            )}
            <FormLayout.MandatoryInfo areAllFieldsMandatory />
            <Callout
              className={styles['offer-educational-stock-banner']}
              links={[
                {
                  href: 'https://passculture.zendesk.com/hc/fr/articles/4412973958673--Acteurs-culturels-Comment-modifier-une-offre-collective-pr%C3%A9-r%C3%A9serv%C3%A9e-',
                  label:
                    'Consultez l’article “Comment modifier ou annuler une offre collective pré-réservée”',
                  isExternal: true,
                },
              ]}
            >
              Vous pouvez modifier ces informations en fonction de vos échanges
              avec l’établissement scolaire tant que le chef d’établissement n’a
              pas validé la réservation.
            </Callout>
            <FormLayout.Section title="Indiquez le prix et la date de votre offre">
              <>
                <p className={styles['description-text']}>
                  Indiquez le prix total TTC de l’évènement et le nombre de
                  personnes qui y participeront.
                  <br />
                  <span className={styles['description-text-example']}>
                    Exemple : j’accueille 30 élèves à 5{NBSP}€ la place, le prix
                    total de mon offre s’élève à 150{NBSP}€ TTC.
                  </span>
                </p>
                <FormStock
                  mode={mode}
                  canEditDiscount={canEditDiscount}
                  canEditDates={canEditDates}
                  preventPriceIncrease={preventPriceIncrease}
                />
              </>

              <FormLayout.Row>
                <TextArea
                  className={styles['price-details']}
                  disabled={!canEditDiscount}
                  label={DETAILS_PRICE_LABEL}
                  maxLength={MAX_PRICE_DETAILS_LENGTH}
                  {...form.register('priceDetail')}
                  description={PRICE_DETAIL_PLACEHOLDER}
                  error={form.formState.errors.priceDetail?.message}
                  asterisk={false}
                  required
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <FormLayout.Section title="Conditions de réservation">
              <>
                <p className={styles['description-text']}>
                  Indiquez la date limite avant laquelle l’offre doit être
                  réservée par l’enseignant puis par le chef d’établissement. À
                  défaut, l’offre expirera et ne sera plus visible sur ADAGE.
                </p>
                <FormLayout.Row>
                  <DatePicker
                    disabled={!canEditDates}
                    label={BOOKING_LIMIT_DATETIME_LABEL}
                    minDate={new Date(offer.dateCreated)}
                    maxDate={
                      isDateValid(new Date(values.startDatetime))
                        ? new Date(values.startDatetime)
                        : undefined
                    }
                    {...form.register('bookingLimitDatetime')}
                    error={form.formState.errors.bookingLimitDatetime?.message}
                    className={styles['input-date']}
                    required
                    asterisk={false}
                  />
                </FormLayout.Row>
              </>
            </FormLayout.Section>
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  to={
                    mode === Mode.CREATION
                      ? `/offre/collectif/${offer.id}/creation${
                          requestId ? `?requete=${requestId}` : ''
                        }`
                      : '/offres/collectives'
                  }
                >
                  {mode === Mode.CREATION ? 'Retour' : 'Annuler et quitter'}
                </ButtonLink>
              </ActionsBarSticky.Left>

              <ActionsBarSticky.Right
                dirtyForm={form.formState.isDirty}
                mode={mode}
              >
                <Button
                  type="submit"
                  disabled={!(canEditDiscount || canEditDates)}
                  isLoading={isLoading}
                >
                  Enregistrer et continuer
                </Button>
              </ActionsBarSticky.Right>
            </ActionsBarSticky>
          </FormLayout>
        </form>
      </FormProvider>
      <RouteLeavingGuardCollectiveOfferCreation
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </>
  )
}
