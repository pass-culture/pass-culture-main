import { Formik } from 'formik'
import React from 'react'
import { Link } from 'react-router-dom'
import cn from 'classnames'

import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { Category, SubCategory } from 'custom_types/categories'
import { SubmitButton } from 'ui-kit'

import styles from './OfferEducational.module.scss'
import FormAccessibitily from './OfferEducationalForm/FormAccessibility'
import FormContact from './OfferEducationalForm/FormContact'
import FormNotifications from './OfferEducationalForm/FormNotifications'
import FormOfferVenue from './OfferEducationalForm/FormOfferVenue'
import FormParticipants from './OfferEducationalForm/FormParticipants'
import FormType from './OfferEducationalForm/FormType'
import FormVenue from './OfferEducationalForm/FormVenue'
import Banner from 'components/layout/Banner/Banner'
import { CGU_URL } from 'utils/config'

interface IOfferEducationalProps {
    educationalCategories: Category[];
    educationalSubcategories: SubCategory[];
    initialValues: Record<string, unknown>;
}

const OfferEducational = ({
  educationalCategories,
  educationalSubcategories,
  initialValues,
}: IOfferEducationalProps): JSX.Element => {
  const categoryInitialValue = educationalCategories[0]?.id
  const subCategoryInitialValue = categoryInitialValue ?
    educationalSubcategories.filter(
      subCategory => subCategory.categoryId === categoryInitialValue)[0]?.id
    : ''

  return (
    <Formik
      enableReinitialize // so that dynamic initial values can be set when available
      initialValues={{ 
        ...initialValues, 
        category: categoryInitialValue, 
        subCategory: subCategoryInitialValue, 
      }}
      onSubmit={() => {return}}
    >
      {({ values }) => {
        return (
          <div className={styles['educational-form']}>
            <p className={styles['educational-form-information']}>
              Tous les champs sont obligatoires sauf mention contraire.
            </p>
            <FormType
              categories={educationalCategories}
              subCategories={educationalSubcategories}
              values={values}
            />
            <FormVenue />
            <FormOfferVenue />
            <FormParticipants />
            <FormAccessibitily />
            <FormContact />
            <FormNotifications />
            <Banner
              href={CGU_URL}
              linkTitle={"Consulter les Conditions Générales d’Utilisation"}
              type="notification-info"
            />
            <section className={styles['educational-form-actions']}>
              <Link
                className={cn(styles['educational-form-actions-action'], "secondary-link")}
                to={computeOffersUrl({})}
              >
                Annuler et quitter
              </Link>
              <SubmitButton
                className={cn(styles['educational-form-actions-action'], "primary-button")}
                disabled={false}
                isLoading={false}
                onClick={() => {return}}
              >
                Étape suivante
              </SubmitButton>
            </section>
          </div>
        )}}
    </Formik>
  )
}

export default OfferEducational
