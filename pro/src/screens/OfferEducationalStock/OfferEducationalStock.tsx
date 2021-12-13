import { useFormik, FormikProvider } from 'formik'
import React from 'react'
import { Link } from 'react-router-dom'

import Banner from 'components/layout/Banner/Banner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { Mode } from 'core/OfferEducational'
import { OfferEducationalStockFormValues } from 'core/OfferEducationalStock/types'
import { Offer } from 'custom_types/offer'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'

import FormStock from './FormStock'
import styles from './OfferEducationalStock.module.scss'
import { isOfferDisabled } from './utils'
import { validationSchema } from './validationSchema'

export interface IOfferEducationalStockProps {
  isEditable?: boolean
  initialValues: OfferEducationalStockFormValues
  offer: Offer
  onSubmit: (offer: Offer, values: OfferEducationalStockFormValues) => void
  mode: Mode
}

const OfferEducationalStock = ({
  isEditable = true,
  initialValues,
  offer,
  onSubmit,
  mode,
}: IOfferEducationalStockProps): JSX.Element => {
  const offerIsDisbaled = isOfferDisabled(offer.status)

  const formik = useFormik({
    initialValues,
    onSubmit: values => onSubmit(offer, values),
    validationSchema: validationSchema,
  })

  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit}>
        <FormLayout>
          <FormLayout.Section title="Date et prix">
            <Banner
              href="#"
              linkTitle="Consulter l’article “Comment modifier une offre collective qui est pré-réservée par un établissement ?”"
              type="notification-info"
            >
              Vous pourrez modifier ces informations en fonction de vos échange
              avec l'établissement scolaire.
            </Banner>
            <p className={styles['description-text']}>
              Indiquez le prix total de l’événement et le nombre de personnes
              qui y participeront.
              <br />
              <span className={styles['description-text-italic']}>
                (Exemple : j’accueille 30 élèves à 5€ la place, le prix total de
                mon offre s'élève à 150€)
              </span>
            </p>
            <FormLayout.Row inline>
              <FormStock isEditable={isEditable} />
            </FormLayout.Row>
          </FormLayout.Section>
          <FormLayout.Actions className={styles['action-section']}>
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
  )
}

export default OfferEducationalStock
