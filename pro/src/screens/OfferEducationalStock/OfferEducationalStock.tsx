/* @debt standard "Gautier: Do not load internal page dependencies"*/
import { addDays, isAfter, isBefore } from 'date-fns'
import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import * as yup from 'yup'

import {
  CollectiveBookingStatus,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from 'components/Banner/BannerPublicApi'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OfferEducationalActions } from 'components/OfferEducationalActions/OfferEducationalActions'
import { MAX_DETAILS_LENGTH } from 'core/OfferEducational/constants'
import {
  OfferEducationalStockFormValues,
  isCollectiveOffer,
  Mode,
  EducationalOfferType,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational/types'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { NBSP } from 'core/shared/constants'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'

import { DETAILS_PRICE_LABEL } from './constants/labels'
import { FormStock } from './FormStock/FormStock'
import styles from './OfferEducationalStock.module.scss'
import {
  generateValidationSchema,
  showcaseOfferValidationSchema,
} from './validationSchema'

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
  const offerIsDisabled = isOfferDisabled(offer.status)
  const [isLoading, setIsLoading] = useState(false)
  const beginningDatetime =
    isCollectiveOffer(offer) && offer.collectiveStock?.beginningDatetime

  const preventPriceIncrease = Boolean(
    isCollectiveOffer(offer) &&
      (offer.lastBookingStatus === CollectiveBookingStatus.CONFIRMED ||
        (offer.lastBookingStatus === CollectiveBookingStatus.USED &&
          beginningDatetime &&
          isBefore(new Date(), addDays(new Date(beginningDatetime), 2))))
  )

  const disablePriceAndParticipantInputs =
    isCollectiveOffer(offer) &&
    mode === Mode.READ_ONLY &&
    Boolean(
      offer.lastBookingStatus === CollectiveBookingStatus.REIMBURSED ||
        (offer.lastBookingStatus === CollectiveBookingStatus.USED &&
          beginningDatetime &&
          isAfter(new Date(), addDays(new Date(beginningDatetime), 2)))
    )

  const postForm = async (values: OfferEducationalStockFormValues) => {
    setIsLoading(true)
    await onSubmit(offer, values)
    setIsLoading(false)
  }

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit: postForm,
    validationSchema: yup.lazy((values: OfferEducationalStockFormValues) => {
      const isShowcase =
        values.educationalOfferType === EducationalOfferType.SHOWCASE
      /* istanbul ignore next: TO FIX remove this condition as we should not have template offer here */
      return isShowcase
        ? showcaseOfferValidationSchema
        : generateValidationSchema(
            preventPriceIncrease,
            initialValues.totalPrice
          )
    }),
  })

  useEffect(() => {
    // update formik values with initial values when initial values
    // are updated after stock update
    resetForm({ values: initialValues })
  }, [initialValues, resetForm])

  return (
    <>
      <OfferEducationalActions
        className={styles.actions}
        isBooked={
          isCollectiveOfferTemplate(offer)
            ? false
            : Boolean(offer.collectiveStock?.isBooked)
        }
        offer={offer}
        mode={mode}
      />
      <FormikProvider value={{ ...formik, resetForm }}>
        <form onSubmit={formik.handleSubmit} noValidate>
          <FormLayout className={styles['offer-educational-stock-form-layout']}>
            {isCollectiveOffer(offer) && offer.isPublicApi && (
              <BannerPublicApi className={styles['banner-space']}>
                Offre importée automatiquement
              </BannerPublicApi>
            )}
            <FormLayout.MandatoryInfo />
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
              variant={CalloutVariant.INFO}
            >
              Vous pouvez modifier ces informations en fonction de vos échanges
              avec l’établissement scolaire tant que le chef d’établissement n’a
              pas validé la réservation.
            </Callout>
            <FormLayout.Section title="Date et prix">
              <>
                <p className={styles['description-text']}>
                  Indiquez le prix total TTC de l’évènement et le nombre de
                  personnes qui y participeront.
                  <br />
                  <span className={styles['description-text-italic']}>
                    (Exemple : j’accueille 30 élèves à 5{NBSP}€ la place, le
                    prix total global de mon offre s’élève à 150{NBSP}€ TTC.)
                  </span>
                </p>
                <FormStock
                  mode={mode}
                  disablePriceAndParticipantInputs={
                    disablePriceAndParticipantInputs
                  }
                  preventPriceIncrease={preventPriceIncrease}
                  offerDateCreated={offer.dateCreated}
                />
              </>
              )
              <FormLayout.Row>
                <TextArea
                  className={styles['price-details']}
                  countCharacters
                  disabled={disablePriceAndParticipantInputs}
                  label={DETAILS_PRICE_LABEL}
                  maxLength={MAX_DETAILS_LENGTH}
                  name="priceDetail"
                  placeholder="Détaillez ici des informations complémentaires."
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to:
                      mode === Mode.CREATION
                        ? `/offre/collectif/${offer.id}/creation${
                            requestId ? `?requete=${requestId}` : ''
                          }`
                        : '/offres/collectives',
                    isExternal: false,
                  }}
                >
                  {mode === Mode.CREATION
                    ? 'Étape précédente'
                    : 'Annuler et quitter'}
                </ButtonLink>
                <Button
                  type="submit"
                  className=""
                  disabled={
                    (offerIsDisabled || mode === Mode.READ_ONLY) &&
                    disablePriceAndParticipantInputs
                  }
                  isLoading={isLoading}
                >
                  {mode !== Mode.CREATION
                    ? 'Enregistrer les modifications'
                    : 'Étape suivante'}
                </Button>
              </ActionsBarSticky.Left>
            </ActionsBarSticky>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}
