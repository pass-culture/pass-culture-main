/* @debt standard "Gautier: Do not load internal page dependencies"*/

import { addDays, isAfter, isBefore } from 'date-fns'
import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as yup from 'yup'

import { CollectiveBookingStatus, StudentLevels } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import BannerPublicApi from 'components/Banner/BannerPublicApi'
import FormLayout from 'components/FormLayout'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalOfferType,
  isCollectiveOffer,
  MAX_DETAILS_LENGTH,
  Mode,
  OfferEducationalStockFormValues,
  OPENING_DATE_FOR_6E_AND_5E,
} from 'core/OfferEducational'
import { isOfferDisabled } from 'core/Offers/utils'
import { Banner, ButtonLink, SubmitButton, TextArea } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { DETAILS_PRICE_LABEL } from './constants/labels'
import FormStock from './FormStock'
import styles from './OfferEducationalStock.module.scss'
import ShowcaseBannerInfo from './ShowcaseBannerInfo'
import {
  generateValidationSchema,
  showcaseOfferValidationSchema,
} from './validationSchema'
import WrongStudentsModal from './WrongStudentsModal/WrongStudentsModal'

export interface IOfferEducationalStockProps<
  T = CollectiveOffer | CollectiveOfferTemplate
> {
  initialValues: OfferEducationalStockFormValues
  offer: T
  onSubmit: (offer: T, values: OfferEducationalStockFormValues) => Promise<void>
  mode: Mode
  reloadCollectiveOffer?: () => void
}

const OfferEducationalStock = <
  T extends CollectiveOffer | CollectiveOfferTemplate
>({
  initialValues,
  offer,
  onSubmit,
  mode,
  reloadCollectiveOffer,
}: IOfferEducationalStockProps<T>): JSX.Element => {
  const offerIsDisabled = isOfferDisabled(offer.status)
  const [isLoading, setIsLoading] = useState(false)
  const [isWrongStudentsModalVisible, setIsWrongStudentsModalVisible] =
    useState(false)
  const navigate = useNavigate()
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

  const hasOnly6eAnd5eStudents = offer.students.every(
    student =>
      student == StudentLevels.COLL_GE_6E || student == StudentLevels.COLL_GE_5E
  )

  const submitForm = async (values: OfferEducationalStockFormValues) => {
    if (
      values.eventDate < OPENING_DATE_FOR_6E_AND_5E &&
      (offer.students.includes(StudentLevels.COLL_GE_6E) ||
        offer.students.includes(StudentLevels.COLL_GE_5E))
    ) {
      setIsWrongStudentsModalVisible(true)
      return
    }
    postForm(values)
  }

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit: submitForm,
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

  const displayElementsForShowcaseOption =
    formik.values.educationalOfferType === EducationalOfferType.SHOWCASE

  return (
    <>
      <OfferEducationalActions
        className={styles.actions}
        isBooked={
          offer.isTemplate ? false : Boolean(offer.collectiveStock?.isBooked)
        }
        offer={offer}
        reloadCollectiveOffer={reloadCollectiveOffer}
        mode={mode}
      />
      <FormikProvider value={{ ...formik, resetForm }}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout className={styles['offer-educational-stock-form-layout']}>
            {isCollectiveOffer(offer) && offer.isPublicApi && (
              <BannerPublicApi className={styles['banner-space']}>
                Offre importée automatiquement
              </BannerPublicApi>
            )}
            <FormLayout.MandatoryInfo />
            <FormLayout.Section title="Date et prix">
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
                    échanges avec l’établissement scolaire.
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
                  <FormStock
                    mode={mode}
                    disablePriceAndParticipantInputs={
                      disablePriceAndParticipantInputs
                    }
                    preventPriceIncrease={preventPriceIncrease}
                    offerDateCreated={offer.dateCreated}
                  />
                </>
              )}
              <FormLayout.Row>
                <TextArea
                  className={styles['price-details']}
                  countCharacters
                  disabled={mode === Mode.READ_ONLY}
                  isOptional
                  label={DETAILS_PRICE_LABEL}
                  maxLength={MAX_DETAILS_LENGTH}
                  name="priceDetail"
                  placeholder="Détaillez ici des informations complémentaires"
                />
              </FormLayout.Row>
            </FormLayout.Section>
            {isWrongStudentsModalVisible && (
              <WrongStudentsModal
                closeModal={() => setIsWrongStudentsModalVisible(false)}
                postForm={() => postForm(formik.values)}
                modifyStudents={() =>
                  navigate(
                    `/offre/collectif/${offer.id}/${
                      mode == Mode.EDITION ? 'edition' : 'creation'
                    }`
                  )
                }
                hasOnlyWrongStudents={hasOnly6eAnd5eStudents}
              />
            )}
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to: `/offre/collectif/${offer.id}/creation`,
                    isExternal: false,
                  }}
                >
                  Étape précédente
                </ButtonLink>
              </ActionsBarSticky.Left>
              <ActionsBarSticky.Right>
                <SubmitButton
                  className=""
                  disabled={
                    (offerIsDisabled || mode === Mode.READ_ONLY) &&
                    disablePriceAndParticipantInputs
                  }
                  isLoading={isLoading}
                >
                  {mode === Mode.EDITION ? 'Enregistrer' : 'Étape suivante'}
                </SubmitButton>
              </ActionsBarSticky.Right>
            </ActionsBarSticky>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}

export default OfferEducationalStock
