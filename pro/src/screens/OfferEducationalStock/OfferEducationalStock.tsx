import { useFormik, FormikProvider } from 'formik'
import React from 'react'
import { Link } from 'react-router-dom'

import Banner from 'components/layout/Banner/Banner'
/* @debt standard "Gautier: Do not load internal page dependencies"*/
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import {
  Mode,
  OfferEducationalStockFormValues,
  GetStockOfferSuccessPayload,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import OfferEducationalActions from 'new_components/OfferEducationalActions'
import { SubmitButton } from 'ui-kit'

import FormStock from './FormStock'
import styles from './OfferEducationalStock.module.scss'
import { isOfferDisabled } from './utils'
import { validationSchema } from './validationSchema'

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
}

const OfferEducationalStock = ({
  initialValues,
  offer,
  onSubmit,
  mode,
  cancelActiveBookings,
  setIsOfferActive,
}: IOfferEducationalStockProps): JSX.Element => {
  const offerIsDisbaled = isOfferDisabled(offer.status)

  const formik = useFormik({
    initialValues,
    onSubmit: values => onSubmit(offer, values),
    validationSchema: validationSchema,
  })

  const shouldShowOfferActions =
    (mode === Mode.EDITION || mode === Mode.READ_ONLY) &&
    setIsOfferActive &&
    cancelActiveBookings

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
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout>
            <FormLayout.Section title="Date et prix">
              <Banner
                href="https://passculture.zendesk.com/hc/fr/articles/4412973958673--Acteurs-culturels-Comment-modifier-une-offre-collective-pr%C3%A9-r%C3%A9serv%C3%A9e-"
                linkTitle="Consultez l’article “Comment modifier une offre collective qui est pré-réservée par un établissement ?”"
                type="notification-info"
              >
                Vous pourrez modifier ces informations en fonction de vos
                échanges avec l'établissement scolaire.
              </Banner>
              <p className={styles['description-text']}>
                Indiquez le prix total de l’événement et le nombre de personnes
                qui y participeront.
                <br />
                <span className={styles['description-text-italic']}>
                  (Exemple : j’accueille 30 élèves à 5€ la place, le prix total
                  de mon offre s'élève à 150€)
                </span>
              </p>
              <FormStock mode={mode} />
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
