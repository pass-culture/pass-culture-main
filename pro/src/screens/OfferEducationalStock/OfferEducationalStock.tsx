import { useFormik, FormikProvider } from 'formik'
import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
/* @debt standard "Gautier: Do not load internal page dependencies"*/
import * as yup from 'yup'

import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import {
  Mode,
  OfferEducationalStockFormValues,
  GetStockOfferSuccessPayload,
  EducationalOfferType,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import OfferEducationalActions from 'new_components/OfferEducationalActions'
import { RadioGroup, SubmitButton, Banner, TextArea } from 'ui-kit'

import { DETAILS_PRICE_LABEL } from './constants/labels'
import FormStock from './FormStock'
import styles from './OfferEducationalStock.module.scss'
import ShowcaseBannerInfo from './ShowcaseBannerInfo'
import { isOfferDisabled } from './utils'
import {
  validationSchema,
  showcaseOfferValidationSchema,
} from './validationSchema'

const showcaseOfferRadios = [
  {
    label: 'Je connais la date et le prix de mon offre',
    value: EducationalOfferType.CLASSIC,
  },
  {
    label:
      'Je préfère être contacté(e) par un enseignant avant de définir la date et le prix de l’offre',
    value: EducationalOfferType.SHOWCASE,
  },
]

export interface IOfferEducationalStockProps {
  isEditable?: boolean
  initialValues: OfferEducationalStockFormValues
  offer: GetStockOfferSuccessPayload
  onSubmit: (
    offer: GetStockOfferSuccessPayload,
    values: OfferEducationalStockFormValues
  ) => void
  mode: Mode
  cancelActiveBookings?: () => void
  setIsOfferActive?: (isActive: boolean) => void
  isShowcaseFeatureEnabled?: boolean
}

const OfferEducationalStock = ({
  initialValues,
  offer,
  onSubmit,
  mode,
  cancelActiveBookings,
  setIsOfferActive,
  isShowcaseFeatureEnabled = false,
}: IOfferEducationalStockProps): JSX.Element => {
  const offerIsDisbaled = isOfferDisabled(offer.status)

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit: values => onSubmit(offer, values),
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

  const displayElementsForShowcaseOption =
    isShowcaseFeatureEnabled &&
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
              {isShowcaseFeatureEnabled && (
                <FormLayout.Row>
                  <RadioGroup
                    group={showcaseOfferRadios}
                    name="educationalOfferType"
                  />
                </FormLayout.Row>
              )}
              {!displayElementsForShowcaseOption && (
                <>
                  {!displayElementsForShowcaseOption && (
                    <div className={styles['separator']} />
                  )}
                  <Banner
                    className={styles['offer-educational-stock-banner']}
                    href="https://passculture.zendesk.com/hc/fr/articles/4412973958673--Acteurs-culturels-Comment-modifier-une-offre-collective-pr%C3%A9-r%C3%A9serv%C3%A9e-"
                    linkTitle="Consultez l’article “Comment modifier ou annuler une offre collective pré-réservée/réservée”"
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
                    Indiquez le prix total de l’événement et le nombre de
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
                  placeholder="Détaillez ici ce que comprend votre prix total"
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <FormLayout.Actions>
              <Link className="secondary-link" to={computeOffersUrl({})}>
                Annuler et quitter
              </Link>
              <SubmitButton
                className=""
                disabled={offerIsDisbaled}
                isLoading={false}
              >
                {mode === Mode.CREATION
                  ? 'Valider et créer l’offre'
                  : 'Enregistrer'}
              </SubmitButton>
            </FormLayout.Actions>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducationalStock
