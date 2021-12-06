import { useFormik, FormikProvider } from 'formik'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import {
  Offer,
  OfferEducationalStockFormValues,
} from 'core/OfferEducationalStock/types'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'

import { OfferStatus } from './constants/offerStatus'
import FormStock from './FormStock'
import styles from './OfferEducationalStock.module.scss'
import { isOfferDisabled } from './utils'
import { validationSchema } from './validationSchema'

export interface IOfferEducationalStockProps {
  initialValues: OfferEducationalStockFormValues
  offer: Offer
  onSubmit: (offer: Offer, values: OfferEducationalStockFormValues) => void
}

const OfferEducationalStock = ({
  initialValues,
  offer,
  onSubmit,
}: IOfferEducationalStockProps): JSX.Element => {
  const isOfferDraft = offer.status === OfferStatus.OFFER_STATUS_DRAFT
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
            <Banner type="notification-info">
              La date et le prix que vous indiquez sont à titre indicatif. Vous
              pouvez par la suite définir toutes les dates réelles avec les
              établissements scolaires.
              <br />
              Suite à votre événement, vous recevrez un mail pour confirmer les
              éléments de votre offre et mettre à jour le nombre de participants
              réels.
            </Banner>
            <p className={styles['description-text']}>
              Indiquez le prix total du nombre de places maximum pour un
              établissement scolaire.
              <br />
              (ex : mon offre s'élève à 200 euros pour 30 places dédiées à un
              établissement scolaire.)
            </p>
            <FormLayout.Row inline>
              <FormStock />
            </FormLayout.Row>
          </FormLayout.Section>
          <FormLayout.Actions className={styles['action-section']}>
            <SubmitButton
              className=""
              disabled={offerIsDisbaled}
              isLoading={false}
            >
              {isOfferDraft ? 'Valider et créer l’offre' : 'Enregistrer'}
            </SubmitButton>
          </FormLayout.Actions>
        </FormLayout>
      </form>
    </FormikProvider>
  )
}

export default OfferEducationalStock
