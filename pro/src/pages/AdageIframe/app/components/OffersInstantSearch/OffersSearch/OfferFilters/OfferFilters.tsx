import { Form, FormikProvider, useFormikContext } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useEffect, useState } from 'react'

import { OfferAddressType } from 'apiClient/adage'
import AdageButtonFilter from 'components/AdageButtonFilter/AdageButtonFilter'
import FormLayout from 'components/FormLayout'
import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeBuildingIcon from 'icons/stroke-building.svg'
import strokeFranceIcon from 'icons/stroke-france.svg'
import strokeSearch from 'icons/stroke-search.svg'
import { getAcademiesOptionsAdapter } from 'pages/AdageIframe/app/adapters/getAcademiesOptionsAdapter'
import { getEducationalCategoriesOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalCategoriesOptionsAdapter'
import { getEducationalDomainsOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalDomainsOptionsAdapter'
import { departmentOptions } from 'pages/AdageIframe/app/constants/departmentOptions'
import { Option } from 'pages/AdageIframe/app/types'
import { Button, RadioGroup, TextInput } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import AdageMultiselect from 'ui-kit/form/AdageMultiselect/AdageMultiselect'

import { ADAGE_FILTERS_DEFAULT_VALUES } from '../../utils'
import { LocalisationFilterStates, SearchFormValues } from '../OffersSearch'

import ModalFilterLayout from './ModalFilterLayout/ModalFilterLayout'
import styles from './OfferFilters.module.scss'
import { studentsOptions } from './studentsOptions'

interface OfferFiltersProps {
  className?: string
  isLoading: boolean
  localisationFilterState: LocalisationFilterStates
  setLocalisationFilterState: (state: LocalisationFilterStates) => void
  resetForm: () => void
}

export const OfferFilters = ({
  className,
  isLoading,
  localisationFilterState,
  setLocalisationFilterState,
  resetForm,
}: OfferFiltersProps): JSX.Element => {
  const [modalOpenStatus, setModalOpenStatus] = useState<{
    [key: string]: boolean
  }>({})

  const formik = useFormikContext<SearchFormValues>()

  const getActiveLocalisationFilterCount = () => {
    if (!formik.values) {
      return 0
    }
    if (localisationFilterState === LocalisationFilterStates.DEPARTMENTS) {
      return formik.values.departments.length
    }
    if (localisationFilterState === LocalisationFilterStates.ACADEMIES) {
      return formik.values.academies.length
    }
    return 0
  }
  const activeLocalisationFilterCount = getActiveLocalisationFilterCount()

  const [domainsOptions, setDomainsOptions] = useState<Option<number>[]>([])
  const [academiesOptions, setAcademieOptions] = useState<Option<string>[]>([])
  const [categoriesOptions, setCategoriesOptions] = useState<
    Option<string[]>[]
  >([])

  const onReset = (
    modalName: string,
    value: string | string[],
    fieldName?: string
  ) => {
    clearFormikFieldValue(fieldName || modalName, value)
    if (modalName === 'localisation') {
      setLocalisationFilterState(LocalisationFilterStates.NONE)
    }
    setModalOpenStatus(prevState => ({ ...prevState, [modalName]: false }))
  }

  const onSearch = (modalName: string) => {
    formik.handleSubmit()
    setModalOpenStatus(prevState => ({ ...prevState, [modalName]: false }))
  }
  useEffect(() => {
    const loadFiltersOptions = async () => {
      const domainsResponse = await getEducationalDomainsOptionsAdapter()
      const academiesResponse = await getAcademiesOptionsAdapter()
      const categoriesResponse = await getEducationalCategoriesOptionsAdapter(
        null
      )

      if (categoriesResponse.isOk) {
        setCategoriesOptions(categoriesResponse.payload.educationalCategories)
      }

      if (domainsResponse.isOk) {
        setDomainsOptions(domainsResponse.payload)
      }
      if (academiesResponse.isOk) {
        setAcademieOptions(academiesResponse.payload)
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
          <div className={styles['filter-container-search']}>
            <TextInput
              label=""
              className={styles['filter-container-search-input']}
              name="query"
              type="search"
              placeholder="Rechercher : nom de l’offre, partenaire culturel"
              hideFooter
              leftIcon={strokeSearch}
            />
            <Button
              disabled={isLoading}
              type="submit"
              className={styles['filter-container-search-button']}
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
                onReset('eventAddressType', OfferAddressType.OTHER)
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
            isActive={
              localisationFilterState !== LocalisationFilterStates.NONE &&
              activeLocalisationFilterCount > 0
            }
            title="Localisation des partenaires"
            itemsLength={activeLocalisationFilterCount}
            isOpen={modalOpenStatus['localisation']}
            setIsOpen={setModalOpenStatus}
            filterName="localisation"
            handleSubmit={formik.handleSubmit}
          >
            {localisationFilterState === LocalisationFilterStates.NONE && (
              <ModalFilterLayout
                title="Dans quelle zone géographique"
                hideFooter
              >
                <ul>
                  <li className={styles['localisation-list-button']}>
                    <Button
                      onClick={() =>
                        setLocalisationFilterState(
                          LocalisationFilterStates.DEPARTMENTS
                        )
                      }
                      variant={ButtonVariant.TERNARY}
                      icon={strokeFranceIcon}
                      iconPosition={IconPositionEnum.LEFT}
                    >
                      Choisir un département
                    </Button>
                  </li>
                  <li className={styles['localisation-list-button']}>
                    <Button
                      onClick={() =>
                        setLocalisationFilterState(
                          LocalisationFilterStates.ACADEMIES
                        )
                      }
                      variant={ButtonVariant.TERNARY}
                      icon={strokeBuildingIcon}
                      iconPosition={IconPositionEnum.LEFT}
                    >
                      Choisir une académie
                    </Button>
                  </li>
                </ul>
              </ModalFilterLayout>
            )}
            {localisationFilterState ===
              LocalisationFilterStates.DEPARTMENTS && (
              <ModalFilterLayout
                onClean={() => onReset('localisation', [], 'departments')}
                onSearch={() => onSearch('localisation')}
                title="Choisir un département"
              >
                <AdageMultiselect
                  placeholder="Ex: 59 ou Hauts-de-France"
                  name="departments"
                  label="Départements"
                  options={departmentOptions}
                  isOpen={modalOpenStatus['localisation']}
                />
              </ModalFilterLayout>
            )}
            {localisationFilterState === LocalisationFilterStates.ACADEMIES && (
              <ModalFilterLayout
                onClean={() => onReset('localisation', [], 'academies')}
                onSearch={() => onSearch('localisation')}
                title="Choisir une académie"
              >
                <AdageMultiselect
                  placeholder="Ex: Nantes"
                  name="academies"
                  label="Académies"
                  options={academiesOptions}
                  isOpen={modalOpenStatus['localisation']}
                />
              </ModalFilterLayout>
            )}
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
              onClean={() => onReset('domains', [])}
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
            isActive={formik.values.categories.length > 0}
            title="Catégorie"
            itemsLength={formik.values.categories.length}
            isOpen={modalOpenStatus['categories']}
            setIsOpen={setModalOpenStatus}
            filterName="categories"
            handleSubmit={formik.handleSubmit}
          >
            <ModalFilterLayout
              onClean={() => onReset('categories', [])}
              onSearch={() => onSearch('categories')}
              title="Choisir une catégorie"
            >
              <AdageMultiselect
                placeholder="Ex: Cinéma"
                name="categories"
                label="Catégorie"
                options={categoriesOptions}
                isOpen={modalOpenStatus['categories']}
              />
            </ModalFilterLayout>
          </AdageButtonFilter>
        </FormLayout.Row>
        <FormLayout.Row className={styles['filter-container-filter']}>
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
              onClean={() => onReset('students', [])}
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

          {
            // TODO : We should use a custom isEqual instead of lodash one
            !isEqual(formik.values, ADAGE_FILTERS_DEFAULT_VALUES) && (
              <Button
                className={styles['filter-container-button-clear']}
                onClick={resetForm}
                icon={fullRefreshIcon}
                variant={ButtonVariant.TERNARY}
              >
                Réinitialiser les filtres
              </Button>
            )
          }
        </FormLayout.Row>
      </Form>
    </FormikProvider>
  )
}
