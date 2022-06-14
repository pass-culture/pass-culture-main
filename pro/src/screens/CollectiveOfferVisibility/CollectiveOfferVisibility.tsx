import { FormikProvider, useFormik } from 'formik'

import FormLayout from 'new_components/FormLayout'
import { Link } from 'react-router-dom'
import RadioGroup from 'ui-kit/form/RadioGroup'
import React from 'react'
import { SubmitButton } from 'ui-kit'
import styles from './CollectiveOfferVisibility.module.scss'

const CollectiveOfferVisibility = () => {
  const formik = useFormik({
    initialValues: { visibility: 'all' },
    onSubmit: () => {},
  })
  const visibilityRadios = [
    {
      label: 'Tous les établissements',
      value: 'all',
    },
    {
      label: 'Un établissement en particulier',
      value: 'one',
    },
  ]
  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit}>
        <FormLayout>
          <FormLayout.Section title="Visibilité de l’offre">
            <p className={styles['description-text']}>
              Les établissements concernés par vos choix seront les seuls à
              pouvoir visualiser et/ou préréserver votre offre sur ADAGE. Vous
              avez jusqu’à la préréservation d’un enseignant pour modifier la
              visibilité de votre offre.
            </p>
            <FormLayout.Row className={styles['row-layout']}>
              <fieldset className={styles['legend']}>
                1. Qui peut visualiser votre offre ?
              </fieldset>
              <RadioGroup
                group={visibilityRadios}
                name="visibility"
                withBorder
              />
            </FormLayout.Row>
          </FormLayout.Section>
          <FormLayout.Actions>
            <Link className="secondary-link" to="">
              Annuler et quitter
            </Link>
            <SubmitButton className="" disabled isLoading={false}>
              Valider et créer l’offre
            </SubmitButton>
          </FormLayout.Actions>
        </FormLayout>
      </form>
    </FormikProvider>
  )
}

export default CollectiveOfferVisibility
