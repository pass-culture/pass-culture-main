import { Form, FormikProvider, useFormik } from 'formik'
import React, { useContext, useEffect, useState } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import AdageButtonFilter from 'components/AdageButtonFilter/AdageButtonFilter'
import FormLayout from 'components/FormLayout'
import { getEducationalDomainsOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalDomainsOptionsAdapter'
import { AnalyticsContext } from 'pages/AdageIframe/app/providers/AnalyticsContextProvider'
import { FacetFiltersContext } from 'pages/AdageIframe/app/providers/FacetFiltersContextProvider'
import { Option } from 'pages/AdageIframe/app/types'
import { Button, TextInput } from 'ui-kit'
import AdageMultiselect from 'ui-kit/form/AdageMultiselect/AdageMultiselect'
import { LOGS_DATA } from 'utils/config'

import { adageFiltersToFacetFilters } from '../../utils'

import ModalFilterLayout from './ModalFilterLayout/ModalFilterLayout'
import styles from './OfferFilters.module.scss'

export interface OfferFiltersProps {
  className?: string
  isLoading: boolean
  refine: SearchBoxProvided['refine']
}

interface SearchFormValues {
  query: string
  domains: Option[]
}

export const OfferFilters = ({
  className,
  isLoading,
  refine,
}: OfferFiltersProps): JSX.Element => {
  const [domainsOptions, setDomainsOptions] = useState<Option<number>[]>([])
  const { setFacetFilters } = useContext(FacetFiltersContext)
  const { setFiltersKeys, setHasClickedSearch } = useContext(AnalyticsContext)

  useEffect(() => {
    const loadFiltersOptions = async () => {
      const domainsResponse = await getEducationalDomainsOptionsAdapter()

      if (domainsResponse.isOk) {
        setDomainsOptions(domainsResponse.payload)
      }
    }

    loadFiltersOptions()
  }, [])

  const handleSubmit = (formValues: SearchFormValues): void => {
    const updatedFilters = adageFiltersToFacetFilters({
      ...formValues,
    })
    setFacetFilters(updatedFilters.queryFilters)
    if (LOGS_DATA) {
      setFiltersKeys(updatedFilters.filtersKeys)
      setHasClickedSearch(true)
    }
    refine(formValues.query)
  }

  const formik = useFormik({
    initialValues: {
      query: '',
      domains: [],
    },
    onSubmit: handleSubmit,
  })

  const clearFormikFieldValue = (fieldName: string) => {
    formik.setFieldValue(fieldName, '')
  }

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
          <AdageButtonFilter
            isActive={formik.values.domains.length > 0}
            title="Domaine artistique"
            itemsLength={formik.values.domains.length}
          >
            <ModalFilterLayout
              onClean={() => clearFormikFieldValue('domains')}
              onSearch={() => handleSubmit(formik.values)}
              title="Choisir un domaine artistique"
            >
              <AdageMultiselect
                placeholder="Ex: Cinéma"
                name="domains"
                label="Domaine artistique"
                options={domainsOptions}
              />
            </ModalFilterLayout>
          </AdageButtonFilter>
        </FormLayout.Row>
      </Form>
    </FormikProvider>
  )
}
