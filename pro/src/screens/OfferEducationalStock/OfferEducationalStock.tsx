/* @debt standard "Gautier: Do not load internal page dependencies"*/

import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import * as yup from 'yup'

import {
  EducationalOfferType,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { computeOffersUrl } from 'core/Offers/utils'
import FormLayout from 'new_components/FormLayout'
import OfferEducationalActions from 'new_components/OfferEducationalActions'
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

const getNextButtonWording = (
  mode: Mode,
  offerType: EducationalOfferType
): string => {
  if (mode === Mode.EDITION) {
    return 'Enregistrer'
  }

  if (offerType === EducationalOfferType.CLASSIC) {
    return 'Étape suivante'
  }

  return 'Valider et créer l’offre'
}

export interface IOfferEducationalStockProps {
  initialValues: OfferEducationalStockFormValues
  offer: GetStockOfferSuccessPayload
  onSubmit: (
    offer: GetStockOfferSuccessPayload,
    values: OfferEducationalStockFormValues
  ) => Promise<void>
  mode: Mode
  cancelActiveBookings?: () => void
  setIsOfferActive?: (isActive: boolean) => void
}

const OfferEducationalStock = ({
  initialValues,
  offer,
  onSubmit,
  mode,
  cancelActiveBookings,
  setIsOfferActive,
}: IOfferEducationalStockProps): JSX.Element => {
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
    mode == Mode.CREATION || (mode == Mode.EDITION && offer.isShowcase)

  const displayElementsForShowcaseOption =
    shouldDisplayShowcaseScreen &&
    formik.values.educationalOfferType === EducationalOfferType.SHOWCASE

  return (
    <>
      {shouldShowOfferActions && (
        <OfferEducationalActions
          cancelActiveBookings={cancelActiveBookings}
          className={styles.actions}
          isBooked={offer.isBooked}
          isOfferActive={offer.isActive}
          setIsOfferActive={setIsOfferActive}
        />
      )}
      <FormikProvider value={{ ...formik, resetForm }}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout className={styles['offer-educational-stock-form-layout']}>
            <FormLayout.Section title="Date et prix">
              {shouldDisplayShowcaseScreen && (
                <FormLayout.Row>
                  <RadioGroup
                    group={showcaseOfferRadios}
                    name="educationalOfferType"
                  />
                </FormLayout.Row>
              )}
              {!displayElementsForShowcaseOption && (
                <>
                  {shouldDisplayShowcaseScreen && (
                    <div className={styles['separator']} />
                  )}
                  <Banner
                    className={styles['offer-educational-stock-banner']}
                    href="https://passculture.zendesk.com/hc/fr/articles/4412973958673--Acteurs-culturels-Comment-modifier-une-offre-collective-pr%C3%A9-r%C3%A9serv%C3%A9e-"
                    linkTitle="Consultez l’article “Comment modifier ou annuler une offre collective préréservée/réservée”"
                    type="notification-info"
                  >
                    Vous pourrez modifier ces informations en fonction de vos
                    échanges avec l'établissement scolaire.
                  </Banner>
                </>
              )}
              {displayElementsForShowcaseOption ? (
                <>
                  <ShowcaseBannerInfo />
                  <div className={styles['separator']} />
                </>
              ) : (
                <>
                  <p className={styles['description-text']}>
                    Indiquez le prix total de l’évènement et le nombre de
                    personnes qui y participeront.
                    <br />
                    <span className={styles['description-text-italic']}>
                      (Exemple : j’accueille 30 élèves à 5€ la place, le prix
                      total de mon offre s'élève à 150€)
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
                {getNextButtonWording(mode, formik.values.educationalOfferType)}
              </SubmitButton>
            </FormLayout.Actions>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducationalStock
