import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import AdageButtonFilter from 'components/AdageButtonFilter/AdageButtonFilter'
import FormLayout from 'components/FormLayout'
import { Button, TextInput } from 'ui-kit'

import ModalFilterLayout from './ModalFilterLayout/ModalFilterLayout'
import styles from './OfferFilters.module.scss'

export interface OfferFiltersProps {
  className?: string
  isLoading: boolean
  refine: SearchBoxProvided['refine']
}

interface SearchFormValues {
  query: string
}

export const OfferFilters = ({
  className,
  isLoading,
  refine,
}: OfferFiltersProps): JSX.Element => {
  const handleSubmit = (formValues: SearchFormValues) => {
    refine(formValues.query)
  }

  const formik = useFormik({
    initialValues: {
      query: '',
    },
    onSubmit: handleSubmit,
  })

  return (
    <FormikProvider value={formik}>
      <Form onSubmit={formik.handleSubmit} className={className}>
        <FormLayout.Row>
          <div className={styles['filter-container']}>
            <TextInput
              label=""
              name="query"
              type="text"
              placeholder="Rechercher : nom de l’offre, partenaire culturel"
            />
            <Button
              disabled={isLoading}
              type="submit"
              className={styles['filter-container-search']}
            >
              Rechercher
            </Button>
          </div>
        </FormLayout.Row>
        <FormLayout.Row>
          <AdageButtonFilter isActive={false} title="Domaine artistique">
            <ModalFilterLayout title="Choisir un domaine artistique">
              {/* Ajouter le MultiSelect d'Antoine*/}
            </ModalFilterLayout>
          </AdageButtonFilter>
        </FormLayout.Row>
      </Form>
    </FormikProvider>
  )
}
