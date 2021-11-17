import cn from 'classnames'
import { Formik } from 'formik'
import React from 'react'
import { Link } from 'react-router-dom'

import Banner from 'components/layout/Banner/Banner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { Category, SubCategory } from 'custom_types/categories'
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
import { OfferEducationalFormValues } from './types'

export interface IOfferEducationalProps {
  educationalCategories: Category[]
  educationalSubcategories: SubCategory[]
  initialValues: OfferEducationalFormValues
}

const OfferEducational = ({
  educationalCategories,
  educationalSubcategories,
  initialValues,
}: IOfferEducationalProps): JSX.Element => {
  const categoryInitialValue = educationalCategories[0]?.id
  const subCategoryInitialValue =
    (categoryInitialValue &&
      educationalSubcategories.find(
        subCategory => subCategory.categoryId === categoryInitialValue
      )?.id) ||
    ''

  return (
    <Formik
      enableReinitialize // so that dynamic initial values can be set when available
      initialValues={{
        ...initialValues,
        category: categoryInitialValue,
        subCategory: subCategoryInitialValue,
      }}
      onSubmit={() => {
        return
      }}
    >
      {({ values, setFieldValue }) => {
        return (
          <div className={styles['educational-form']}>
            <p className={styles['educational-form-information']}>
              Tous les champs sont obligatoires sauf mention contraire.
            </p>
            <FormType
              categories={educationalCategories}
              setFieldValue={setFieldValue}
              subCategories={educationalSubcategories}
              values={values}
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
            <section className={styles['educational-form-actions']}>
              <Link
                className={cn(
                  styles['educational-form-action'],
                  'secondary-link'
                )}
                to={computeOffersUrl({})}
              >
                Annuler et quitter
              </Link>
              <SubmitButton
                className={cn(
                  styles['educational-form-action'],
                  'primary-button'
                )}
                disabled={false}
                isLoading={false}
                onClick={() => {
                  return
                }}
              >
                Étape suivante
              </SubmitButton>
            </section>
          </div>
        )
      }}
    </Formik>
  )
}

export default OfferEducational
