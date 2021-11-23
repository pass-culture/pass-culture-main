import { useFormik } from 'formik'
import React from 'react'
import { Link } from 'react-router-dom'

import Banner from 'components/layout/Banner/Banner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { Category, SubCategory } from 'custom_types/categories'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'
import { CGU_URL } from 'utils/config'

import styles from './OfferEducational.module.scss'
import {
  FormAccessibility,
  FormContact,
  FormNotifications,
  FormOfferVenue,
  FormParticipants,
  FormType,
  FormVenue,
} from './OfferEducationalForm'

export interface IOfferEducationalProps {
  educationalCategories: Category[]
  educationalSubcategories: SubCategory[]
  initialValues: OfferEducationalFormValues
  onSubmit(values: OfferEducationalFormValues): void
}

const OfferEducational = ({
  educationalCategories,
  educationalSubcategories,
  initialValues,
  onSubmit,
}: IOfferEducationalProps): JSX.Element => {
  const categoryInitialValue = educationalCategories[0]?.id
  const subCategoryInitialValue =
    (categoryInitialValue &&
      educationalSubcategories.find(
        subCategory => subCategory.categoryId === categoryInitialValue
      )?.id) ||
    ''

  const formik = useFormik({
    initialValues: {
      ...initialValues,
      category: categoryInitialValue,
      subCategory: subCategoryInitialValue,
    },
    onSubmit,
  })

  return (
    <form onSubmit={formik.handleSubmit}>
      <FormLayout className={styles['educational-form']}>
        <p className={styles['educational-form-information']}>
          Tous les champs sont obligatoires sauf mention contraire.
        </p>
        <FormType
          categories={educationalCategories}
          setFieldValue={formik.setFieldValue}
          subCategories={educationalSubcategories}
          values={formik.values}
        />
        <FormVenue />
        <FormOfferVenue />
        <FormParticipants />
        <FormAccessibility />
        <FormContact />
        <FormNotifications />
        <Banner
          href={CGU_URL}
          linkTitle="Consulter les Conditions Générales d’Utilisation"
          type="notification-info"
        />
        <FormLayout.Actions>
          <Link className="secondary-link" to={computeOffersUrl({})}>
            Annuler et quitter
          </Link>
          <SubmitButton
            className="primary-button"
            disabled={false}
            isLoading={false}
            onClick={() => {
              return
            }}
          >
            Étape suivante
          </SubmitButton>
        </FormLayout.Actions>
      </FormLayout>
    </form>
  )
}

export default OfferEducational
