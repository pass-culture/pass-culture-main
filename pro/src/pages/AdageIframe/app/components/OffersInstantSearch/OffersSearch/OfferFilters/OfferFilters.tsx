import { Form, FormikProvider, useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import AdageButtonFilter from 'components/AdageButtonFilter/AdageButtonFilter'
import FormLayout from 'components/FormLayout'
import fullClear from 'icons/full-clear.svg'
import { getEducationalDomainsOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalDomainsOptionsAdapter'
import { Option } from 'pages/AdageIframe/app/types'
import { Button, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import AdageMultiselect from 'ui-kit/form/AdageMultiselect/AdageMultiselect'

import { SearchFormValues } from '../OffersSearch'

import ModalFilterLayout from './ModalFilterLayout/ModalFilterLayout'
import styles from './OfferFilters.module.scss'
import { studentsOptions } from './studentsOptions'

export interface OfferFiltersProps {
  className?: string
  isLoading: boolean
}

export const OfferFilters = ({
  className,
  isLoading,
}: OfferFiltersProps): JSX.Element => {
  const [modalOpenStatus, setModalOpenStatus] = useState<{
    [key: string]: boolean
  }>({})
  const [domainsOptions, setDomainsOptions] = useState<Option<number>[]>([])

  const formik = useFormikContext<SearchFormValues>()

  const onClean = (modalName: string) => {
    clearFormikFieldValue(modalName)
    setModalOpenStatus(prevState => ({ ...prevState, [modalName]: false }))
  }

  const onSearch = (modalName: string) => {
    formik.handleSubmit()
    setModalOpenStatus(prevState => ({ ...prevState, [modalName]: false }))
  }

  useEffect(() => {
    const loadFiltersOptions = async () => {
      const domainsResponse = await getEducationalDomainsOptionsAdapter()

      if (domainsResponse.isOk) {
        setDomainsOptions(domainsResponse.payload)
      }
    }

    loadFiltersOptions()
  }, [])

  const clearFormikFieldValue = (fieldName: string) => {
    formik.setFieldValue(fieldName, [])
    formik.handleSubmit()
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
        <FormLayout.Row className={styles['filter-container-filter']}>
          <AdageButtonFilter
            isActive={formik.values.domains.length > 0}
            title="Domaine artistique"
            itemsLength={formik.values.domains.length}
            isOpen={modalOpenStatus['domains']}
            setIsOpen={setModalOpenStatus}
            filterName="domains"
            handleSubmit={formik.handleSubmit}
          >
            <ModalFilterLayout
              onClean={() => onClean('domains')}
              onSearch={() => onSearch('domains')}
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
          <AdageButtonFilter
            isActive={formik.values.students.length > 0}
            title="Niveau scolaire"
            itemsLength={formik.values.students.length}
            isOpen={modalOpenStatus['students']}
            setIsOpen={setModalOpenStatus}
            filterName="students"
            handleSubmit={formik.handleSubmit}
          >
            <ModalFilterLayout
              onClean={() => onClean('students')}
              onSearch={() => onSearch('students')}
              title="Pour quel niveau scolaire ?"
            >
              <AdageMultiselect
                placeholder="Ex: Collège"
                name="students"
                label="Niveau scolaire"
                options={studentsOptions}
              />
            </ModalFilterLayout>
          </AdageButtonFilter>
          <Button
            onClick={formik.handleReset}
            icon={fullClear}
            variant={ButtonVariant.TERNARY}
            disabled={formik.values === formik.initialValues}
          >
            Effacer les filtres
          </Button>
        </FormLayout.Row>
      </Form>
    </FormikProvider>
  )
}
