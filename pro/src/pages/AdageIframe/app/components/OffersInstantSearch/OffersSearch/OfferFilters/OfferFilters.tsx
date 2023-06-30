import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import FormLayout from 'components/FormLayout'
import { Button, TextInput } from 'ui-kit'

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
      </Form>
    </FormikProvider>
  )
}
