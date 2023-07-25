import { Form, FormikProvider, useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useEffect, useState } from 'react'

import { OfferAddressType } from 'apiClient/adage'
import AdageButtonFilter from 'components/AdageButtonFilter/AdageButtonFilter'
import FormLayout from 'components/FormLayout'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { getEducationalDomainsOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalDomainsOptionsAdapter'
import { Option } from 'pages/AdageIframe/app/types'
import { Button, RadioGroup, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import AdageMultiselect from 'ui-kit/form/AdageMultiselect/AdageMultiselect'

import { SearchFormValues } from '../OffersSearch'

import ModalFilterLayout from './ModalFilterLayout/ModalFilterLayout'
import styles from './OfferFilters.module.scss'
import { studentsOptions } from './studentsOptions'

interface OfferFiltersProps {
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

  const onClean = (modalName: string, value: string | string[]) => {
    clearFormikFieldValue(modalName, value)
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

  const clearFormikFieldValue = (
    fieldName: string,
    value: string | string[]
  ) => {
    formik.setFieldValue(fieldName, value)
    formik.handleSubmit()
  }

  const adressTypeRadios = [
    {
      label: 'Je n’ai pas de préférence (Voir tout)',
      value: OfferAddressType.OTHER,
    },
    {
      label: 'Sortie chez un partenaire culturel',
      value: OfferAddressType.OFFERER_VENUE,
    },
    {
      label: 'Intervention d’un partenaire culturel dans mon établissement',
      value: OfferAddressType.SCHOOL,
    },
  ]

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
            isActive={
              formik.values.eventAddressType.length > 0 &&
              formik.values.eventAddressType !== OfferAddressType.OTHER
            }
            title="Type d’intervention"
            itemsLength={
              formik.values.eventAddressType &&
              formik.values.eventAddressType !== OfferAddressType.OTHER
                ? 1
                : null
            }
            isOpen={modalOpenStatus['eventAddressType']}
            setIsOpen={setModalOpenStatus}
            filterName="eventAddressType"
            handleSubmit={formik.handleSubmit}
          >
            <ModalFilterLayout
              onClean={() =>
                onClean('eventAddressType', OfferAddressType.OTHER)
              }
              onSearch={() => onSearch('eventAddressType')}
            >
              <RadioGroup
                group={adressTypeRadios}
                className={styles['filter-container-evenement']}
                name="eventAddressType"
              />
            </ModalFilterLayout>
          </AdageButtonFilter>
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
              onClean={() => onClean('domains', [])}
              onSearch={() => onSearch('domains')}
              title="Choisir un domaine artistique"
            >
              <AdageMultiselect
                placeholder="Ex: Cinéma"
                name="domains"
                label="Domaine artistique"
                options={domainsOptions}
                isOpen={modalOpenStatus['domains']}
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
              onClean={() => onClean('students', [])}
              onSearch={() => onSearch('students')}
              title="Pour quel niveau scolaire ?"
            >
              <AdageMultiselect
                placeholder="Ex: Collège"
                name="students"
                label="Niveau scolaire"
                options={studentsOptions}
                isOpen={modalOpenStatus['students']}
              />
            </ModalFilterLayout>
          </AdageButtonFilter>
        </FormLayout.Row>
        {!isEqual(formik.values, formik.initialValues) && (
          <Button
            className={styles['filter-container-button-clear']}
            onClick={formik.handleReset}
            icon={fullRefreshIcon}
            variant={ButtonVariant.TERNARY}
          >
            Réinitialiser les filtres
          </Button>
        )}
      </Form>
    </FormikProvider>
  )
}
