/* @debt standard "Gautier: Do not load internal page dependencies"*/

import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  type GetCollectiveOfferResponseModel,
} from '@/apiClient/v1/new'
import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import {
  Mode,
  type OfferEducationalStockFormValues,
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
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
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

export interface OfferEducationalStockProps {
  initialValues: OfferEducationalStockFormValues
  offer: GetCollectiveOfferResponseModel
  onSubmit: (
    offer: GetCollectiveOfferResponseModel,
    values: OfferEducationalStockFormValues
  ) => Promise<void>
  mode: Mode
  requestId?: string | null
}

export const OfferEducationalStock = ({
  initialValues,
  offer,
  onSubmit,
  mode,
  requestId = '',
}: OfferEducationalStockProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)

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
    try {
      await onSubmit(offer, values)
    } catch (error) {
      if (isErrorAPIError(error) && error.status < 500) {
        serializeApiErrors(error.body, form.setError)
      }
    }
    setIsLoading(false)
  }

  const form = useForm({
    defaultValues: initialValues,
    resolver: yupResolver<OfferEducationalStockFormValues, unknown, unknown>(
      generateValidationSchema(offer.allowedActions, initialValues.totalPrice)
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
            {offer.isPublicApi && (
              <BannerPublicApi className={styles['banner-space']} />
            )}
            <FormLayout.MandatoryInfo />
            <div className={styles['offer-educational-stock-banner']}>
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
            <FormLayout.Section title="Indiquez le prix et la date de votre offre">
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
              />

              <FormLayout.Row>
                <TextArea
                  className={styles['price-details']}
                  disabled={!canEditDiscount}
                  label={DETAILS_PRICE_LABEL}
                  maxLength={MAX_PRICE_DETAILS_LENGTH}
                  {...form.register('priceDetail')}
                  description={PRICE_DETAIL_PLACEHOLDER}
                  error={form.formState.errors.priceDetail?.message}
                  requiredIndicator="symbol"
                  required
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <FormLayout.Section title="Conditions de réservation">
              <p className={styles['description-text']}>
                Indiquez la date limite avant laquelle l’offre doit être
                réservée par l’enseignant puis par le chef d’établissement. À
                défaut, l’offre expirera et ne sera plus visible sur ADAGE.
              </p>
              <FormLayout.Row>
                <DatePicker
                  disabled={!canEditDates}
                  label={BOOKING_LIMIT_DATETIME_LABEL}
                  minDate={new Date()}
                  maxDate={
                    isDateValid(new Date(values.startDate))
                      ? new Date(values.startDate)
                      : undefined
                  }
                  {...form.register('bookingLimitDate')}
                  error={form.formState.errors.bookingLimitDate?.message}
                  className={styles['input-date']}
                  required
                  requiredIndicator="symbol"
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <Button
                  as="a"
                  variant={ButtonVariant.SECONDARY}
                  color={
                    mode === Mode.CREATION
                      ? ButtonColor.BRAND
                      : ButtonColor.NEUTRAL
                  }
                  to={
                    mode === Mode.CREATION
                      ? `/offre/collectif/${offer.id}/creation${
                          requestId ? `?requete=${requestId}` : ''
                        }`
                      : '/offres/collectives'
                  }
                  label={
                    mode === Mode.CREATION ? 'Retour' : 'Annuler et quitter'
                  }
                />
              </ActionsBarSticky.Left>

              <ActionsBarSticky.Right
                dirtyForm={form.formState.isDirty}
                mode={mode}
              >
                <Button
                  type="submit"
                  disabled={!(canEditDiscount || canEditDates)}
                  isLoading={isLoading}
                  label="Enregistrer et continuer"
                />
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
