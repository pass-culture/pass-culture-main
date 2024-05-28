import { Form, FormikProvider, useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { AdageFrontRoles, EacFormat, OfferAddressType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { AdageButtonFilter } from 'components/AdageButtonFilter/AdageButtonFilter'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeBuildingIcon from 'icons/stroke-building.svg'
import strokeFranceIcon from 'icons/stroke-france.svg'
import strokeNearIcon from 'icons/stroke-near.svg'
import { departmentOptions } from 'pages/AdageIframe/app/constants/departmentOptions'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { Option } from 'pages/AdageIframe/app/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { AdageMultiselect } from 'ui-kit/form/AdageMultiselect/AdageMultiselect'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { Slider } from 'ui-kit/form/Slider/Slider'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

import { SearchFormValues } from '../../OffersInstantSearch'
import { LocalisationFilterStates } from '../OffersSearch'

import ModalFilterLayout from './ModalFilterLayout/ModalFilterLayout'
import styles from './OfferFilters.module.scss'
import { studentsOptions } from './studentsOptions'

interface OfferFiltersProps {
  className?: string
  localisationFilterState: LocalisationFilterStates
  setLocalisationFilterState: (state: LocalisationFilterStates) => void
  domainsOptions: Option<number>[]
  shouldDisplayMarseilleStudentOptions: boolean
}

export const OfferFilters = ({
  className,
  localisationFilterState,
  setLocalisationFilterState,
  domainsOptions,
  shouldDisplayMarseilleStudentOptions,
}: OfferFiltersProps): JSX.Element => {
  const [modalOpenStatus, setModalOpenStatus] = useState<{
    [key: string]: boolean
  }>({})

  const formik = useFormikContext<SearchFormValues>()

  const { adageUser } = useAdageUser()

  const adageUserHasValidGeoloc =
    (adageUser.lat || adageUser.lat === 0) &&
    (adageUser.lon || adageUser.lon === 0)

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

  const resetLocalisationFilterState = () => {
    if (
      (localisationFilterState === LocalisationFilterStates.DEPARTMENTS &&
        formik.values.departments.length === 0) ||
      (localisationFilterState === LocalisationFilterStates.ACADEMIES &&
        formik.values.academies.length === 0)
    ) {
      setLocalisationFilterState(LocalisationFilterStates.NONE)
    }
  }

  const activeLocalisationFilterCount = getActiveLocalisationFilterCount()

  const [academiesOptions, setAcademieOptions] = useState<Option[]>([])
  const [formatsOptions] = useState<Option<EacFormat>[]>(
    Object.values(EacFormat).map((format) => ({
      value: format,
      label: format,
    }))
  )

  const onReset = async (
    modalName: string,
    value: string | string[] | number,
    fieldName?: string,
    closeModal: boolean = true
  ) => {
    await clearFormikFieldValue(fieldName || modalName, value)
    if (modalName === 'localisation') {
      setLocalisationFilterState(LocalisationFilterStates.NONE)
    }
    if (closeModal) {
      setModalOpenStatus((prevState) => ({ ...prevState, [modalName]: false }))
    }
  }

  const onSearch = (modalName: string) => {
    formik.handleSubmit()
    setModalOpenStatus((prevState) => ({ ...prevState, [modalName]: false }))

    resetLocalisationFilterState()
  }
  useEffect(() => {
    const loadFiltersOptions = async () => {
      try {
        const academies = await apiAdage.getAcademies()
        setAcademieOptions(
          academies.map((academy) => ({
            value: academy,
            label: academy,
          }))
        )
      } catch (e) {
        sendSentryCustomError(e)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadFiltersOptions()
  }, [])

  const clearFormikFieldValue = async (
    fieldName: string,
    value: string | string[] | number
  ) => {
    await formik.setFieldValue(fieldName, value)
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

  const studentsOptionsFiltered = shouldDisplayMarseilleStudentOptions
    ? studentsOptions
    : studentsOptions.filter(
        ({ value }) =>
          value !== 'Écoles Marseille - Maternelle' &&
          value !== 'Écoles Marseille - CP, CE1, CE2' &&
          value !== 'Écoles Marseille - CM1, CM2'
      )

  return (
    <FormikProvider value={formik}>
      <Form onSubmit={formik.handleSubmit} className={className}>
        <FormLayout.Row className={styles['filter-container-buttons']}>
          <div className={styles['filter-container-buttons-list']}>
            <div className={styles['filter-container-buttons-list-items']}>
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
                  (localisationFilterState !== LocalisationFilterStates.NONE &&
                    activeLocalisationFilterCount > 0) ||
                  localisationFilterState ===
                    LocalisationFilterStates.GEOLOCATION
                }
                title="Localisation des partenaires"
                itemsLength={
                  localisationFilterState ===
                  LocalisationFilterStates.GEOLOCATION
                    ? 1
                    : activeLocalisationFilterCount
                }
                isOpen={modalOpenStatus['localisation']}
                setIsOpen={setModalOpenStatus}
                filterName="localisation"
                handleSubmit={() => {
                  resetLocalisationFilterState()
                  formik.handleSubmit()
                }}
              >
                {localisationFilterState === LocalisationFilterStates.NONE && (
                  <ModalFilterLayout
                    title="Dans quelle zone géographique"
                    hideFooter
                  >
                    <ul>
                      {adageUserHasValidGeoloc && (
                        <li className={styles['localisation-list-button']}>
                          <Button
                            onClick={() =>
                              setLocalisationFilterState(
                                LocalisationFilterStates.GEOLOCATION
                              )
                            }
                            disabled={
                              adageUser.role === AdageFrontRoles.READONLY
                            }
                            variant={ButtonVariant.TERNARY}
                            icon={strokeNearIcon}
                          >
                            Autour de mon établissement scolaire
                          </Button>
                        </li>
                      )}
                      <li className={styles['localisation-list-button']}>
                        <Button
                          onClick={() =>
                            setLocalisationFilterState(
                              LocalisationFilterStates.DEPARTMENTS
                            )
                          }
                          variant={ButtonVariant.TERNARY}
                          icon={strokeFranceIcon}
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
                    onClean={() =>
                      onReset('localisation', [], 'departments', false)
                    }
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
                {localisationFilterState ===
                  LocalisationFilterStates.ACADEMIES && (
                  <ModalFilterLayout
                    onClean={() =>
                      onReset('localisation', [], 'academies', false)
                    }
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
                {localisationFilterState ===
                  LocalisationFilterStates.GEOLOCATION && (
                  <ModalFilterLayout
                    onClean={() =>
                      onReset('localisation', 50, 'geolocRadius', false)
                    }
                    onSearch={() => onSearch('localisation')}
                    title="Autour de mon établissement scolaire"
                  >
                    <div className={styles['geoloc-slider']}>
                      <Slider
                        fieldName="geolocRadius"
                        label="Dans un rayon de"
                        scale="km"
                        min={1}
                        max={100}
                        displayValue={true}
                      />
                    </div>
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
                isActive={formik.values.formats.length > 0}
                title="Format"
                itemsLength={formik.values.formats.length}
                isOpen={modalOpenStatus['formats']}
                setIsOpen={setModalOpenStatus}
                filterName="formats"
                handleSubmit={formik.handleSubmit}
              >
                <ModalFilterLayout
                  onClean={() => onReset('formats', [])}
                  onSearch={() => onSearch('formats')}
                  title="Choisir un format"
                >
                  <AdageMultiselect
                    placeholder="Ex: Représentation"
                    name="formats"
                    label="Format"
                    options={formatsOptions}
                    isOpen={modalOpenStatus['formats']}
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
                  onClean={() => onReset('students', [])}
                  onSearch={() => onSearch('students')}
                  title="Pour quel niveau scolaire ?"
                >
                  <AdageMultiselect
                    placeholder="Ex: Collège"
                    name="students"
                    label="Niveau scolaire"
                    options={studentsOptionsFiltered}
                    isOpen={modalOpenStatus['students']}
                    sortOptions={(options, selectedOptions) => {
                      //  Implement custom sort to not sort results alphabetically
                      return [...options].sort((option1, option2) => {
                        const isSelected1 = selectedOptions.includes(
                          option1.value
                        )
                        const isSelected2 = selectedOptions.includes(
                          option2.value
                        )
                        return isSelected1 === isSelected2
                          ? 0
                          : isSelected1 && !isSelected2
                            ? -1
                            : 1
                      })
                    }}
                  />
                </ModalFilterLayout>
              </AdageButtonFilter>
            </div>
          </div>
        </FormLayout.Row>
      </Form>
    </FormikProvider>
  )
}
