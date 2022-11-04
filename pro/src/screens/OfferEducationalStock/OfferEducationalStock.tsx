/* @debt standard "Gautier: Do not load internal page dependencies"*/

import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import * as yup from 'yup'

import FormLayout from 'components/FormLayout'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { computeOffersUrl } from 'core/Offers/utils'
import { Banner, RadioGroup, SubmitButton, TextArea } from 'ui-kit'

import { DETAILS_PRICE_LABEL } from './constants/labels'
import FormStock from './FormStock'
import styles from './OfferEducationalStock.module.scss'
import ShowcaseBannerInfo from './ShowcaseBannerInfo'
import { isOfferDisabled } from './utils'
import {
  showcaseOfferValidationSchema,
  validationSchema,
} from './validationSchema'

const showcaseOfferRadios = [
  {
    label: 'Je connais la date et le prix de mon offre',
    value: EducationalOfferType.CLASSIC,
  },
  {
    label:
      'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre',
    value: EducationalOfferType.SHOWCASE,
  },
]

export interface IOfferEducationalStockProps<
  T = CollectiveOffer | CollectiveOfferTemplate
> {
  initialValues: OfferEducationalStockFormValues
  isCreatingFromTemplate?: boolean
  offer: T
  onSubmit: (offer: T, values: OfferEducationalStockFormValues) => Promise<void>
  mode: Mode
  cancelActiveBookings?: () => void
  setIsOfferActive?: (isActive: boolean) => void
}

const OfferEducationalStock = <
  T extends CollectiveOffer | CollectiveOfferTemplate
>({
  initialValues,
  isCreatingFromTemplate = false,
  offer,
  onSubmit,
  mode,
  cancelActiveBookings,
  setIsOfferActive,
}: IOfferEducationalStockProps<T>): JSX.Element => {
  const offerIsDisabled = isOfferDisabled(offer.status)
  const [isLoading, setIsLoading] = useState(false)

  const submitForm = async (values: OfferEducationalStockFormValues) => {
    setIsLoading(true)
    await onSubmit(offer, values)
    setIsLoading(false)
  }

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit: submitForm,
    validationSchema: yup.lazy((values: OfferEducationalStockFormValues) => {
      const isShowcase =
        values.educationalOfferType === EducationalOfferType.SHOWCASE

      return isShowcase ? showcaseOfferValidationSchema : validationSchema
    }),
  })

  const shouldShowOfferActions =
    (mode === Mode.EDITION || mode === Mode.READ_ONLY) &&
    setIsOfferActive &&
    cancelActiveBookings

  useEffect(() => {
    // update formik values with initial values when initial values
    // are updated after stock update
    resetForm({ values: initialValues })
  }, [initialValues, resetForm])

  const shouldDisplayShowcaseScreen =
    !isCreatingFromTemplate && mode == Mode.CREATION

  const displayElementsForShowcaseOption =
    formik.values.educationalOfferType === EducationalOfferType.SHOWCASE

  return (
    <>
      {shouldShowOfferActions && (
        <OfferEducationalActions
          cancelActiveBookings={cancelActiveBookings}
          className={styles.actions}
          isBooked={
            offer.isTemplate ? false : Boolean(offer.collectiveStock?.isBooked)
          }
          isCancellable={offer.isCancellable}
          isOfferActive={offer.isActive}
          setIsOfferActive={setIsOfferActive}
        />
      )}
      <FormikProvider value={{ ...formik, resetForm }}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout className={styles['offer-educational-stock-form-layout']}>
            <FormLayout.MandatoryInfo />
            <FormLayout.Section title="Date et prix">
              {shouldDisplayShowcaseScreen && (
                <FormLayout.Row>
                  <RadioGroup
                    group={showcaseOfferRadios}
                    name="educationalOfferType"
                    hideFooter
                  />
                </FormLayout.Row>
              )}
              {displayElementsForShowcaseOption ? (
                <ShowcaseBannerInfo />
              ) : (
                <>
                  <Banner
                    className={styles['offer-educational-stock-banner']}
                    links={[
                      {
                        href: 'https://passculture.zendesk.com/hc/fr/articles/4412973958673--Acteurs-culturels-Comment-modifier-une-offre-collective-pr%C3%A9-r%C3%A9serv%C3%A9e-',
                        linkTitle:
                          'Consultez l’article “Comment modifier ou annuler une offre collective préréservée/réservée”',
                      },
                    ]}
                    type="notification-info"
                  >
                    Vous pourrez modifier ces informations en fonction de vos
                    échanges avec l'établissement scolaire.
                  </Banner>
                  <p className={styles['description-text']}>
                    Indiquez le prix global TTC de l’évènement et le nombre de
                    personnes qui y participeront.
                    <br />
                    <span className={styles['description-text-italic']}>
                      (Exemple : j’accueille 30 élèves à 5€ la place, le prix
                      global de mon offre s'élève à 150€ TTC)
                    </span>
                  </p>
                  <FormStock mode={mode} />
                </>
              )}
              <FormLayout.Row>
                <TextArea
                  className={styles['price-details']}
                  countCharacters
                  disabled={mode === Mode.READ_ONLY}
                  isOptional
                  label={DETAILS_PRICE_LABEL}
                  maxLength={1000}
                  name="priceDetail"
                  placeholder="Détaillez ici des informations complémentaires"
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <FormLayout.Actions>
              <Link className="secondary-link" to={computeOffersUrl({})}>
                Annuler et quitter
              </Link>
              <SubmitButton
                className=""
                disabled={offerIsDisabled || mode === Mode.READ_ONLY}
                isLoading={isLoading}
              >
                {mode === Mode.EDITION ? 'Enregistrer' : 'Étape suivante'}
              </SubmitButton>
            </FormLayout.Actions>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducationalStock
