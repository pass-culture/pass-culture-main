import { Form, FormikProvider, useFormikContext } from 'formik'
import { useState } from 'react'
import useSWR from 'swr'

import {
  AdageFrontRoles,
  CollectiveLocationType,
  EacFormat,
  OfferAddressType,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { GET_COLLECTIVE_ACADEMIES } from 'commons/config/swrQueryKeys'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeBuildingIcon from 'icons/stroke-building.svg'
import strokeFranceIcon from 'icons/stroke-france.svg'
import strokeNearIcon from 'icons/stroke-near.svg'
import { departmentOptions } from 'pages/AdageIframe/app/constants/departmentOptions'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'
import { Option } from 'pages/AdageIframe/app/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Slider } from 'ui-kit/form/Slider/Slider'
import {
  AdageMultiselect,
  ItemProps,
} from 'ui-kit/formV2/AdageMultiselect/AdageMultiselect'
import {
  RadioGroup,
  RadioGroupProps,
} from 'ui-kit/formV2/RadioGroup/RadioGroup'

import { SearchFormValues } from '../../OffersInstantSearch'
import { LocalisationFilterStates } from '../OffersSearch'

import { AdageButtonFilter } from './AdageButtonFilter/AdageButtonFilter'
import { ModalFilterLayout } from './ModalFilterLayout/ModalFilterLayout'
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
  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const { adageUser } = useAdageUser()

  const adageUserHasValidGeoloc =
    (adageUser.lat || adageUser.lat === 0) &&
    (adageUser.lon || adageUser.lon === 0)

  const getActiveLocalisationFilterCount = () => {
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

  const { data } = useSWR(
    [GET_COLLECTIVE_ACADEMIES],
    () => apiAdage.getAcademies(),
    { fallbackData: [] }
  )

  const academiesOptions: ItemProps[] = data.map((academy) => ({
    value: academy,
    label: academy,
  }))

  const clearFormikFieldValue = async (
    fieldName: string,
    value: string | string[] | number
  ) => {
    await formik.setFieldValue(fieldName, value)
    formik.handleSubmit()
  }

  const adressTypeRadios: RadioGroupProps['group'] = [
    {
      label: 'Je n’ai pas de préférence (Voir tout)',
      sizing: 'fill',
      value: isCollectiveOaActive
        ? CollectiveLocationType.TO_BE_DEFINED
        : OfferAddressType.OTHER,
    },
    {
      label: 'Sortie chez un partenaire culturel',
      sizing: 'fill',
      value: isCollectiveOaActive
        ? CollectiveLocationType.ADDRESS
        : OfferAddressType.OFFERER_VENUE,
    },
    {
      label: 'Intervention d’un partenaire culturel dans mon établissement',
      sizing: 'fill',
      value: isCollectiveOaActive
        ? CollectiveLocationType.SCHOOL
        : OfferAddressType.SCHOOL,
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

  const setMultiselectValue = async (
    name: string,
    value: ItemProps['value'][]
  ) => {
    await formik.setFieldValue(name, value)
  }

  return (
    <FormikProvider value={formik}>
      <Form onSubmit={formik.handleSubmit} className={className}>
        <FormLayout.Row className={styles['filter-container-buttons']}>
          <div className={styles['filter-container-buttons-list']}>
            <div className={styles['filter-container-buttons-list-items']}>
              <AdageButtonFilter
                isActive={
                  isCollectiveOaActive
                    ? formik.values.locationType.length > 0 &&
                      formik.values.locationType !==
                        CollectiveLocationType.TO_BE_DEFINED
                    : formik.values.eventAddressType.length > 0 &&
                      formik.values.eventAddressType !== OfferAddressType.OTHER
                }
                title="Type d’intervention"
                itemsLength={
                  isCollectiveOaActive
                    ? formik.values.locationType &&
                      formik.values.locationType !==
                        CollectiveLocationType.TO_BE_DEFINED
                      ? 1
                      : null
                    : formik.values.eventAddressType &&
                        formik.values.eventAddressType !==
                          OfferAddressType.OTHER
                      ? 1
                      : null
                }
                isOpen={
                  isCollectiveOaActive
                    ? modalOpenStatus['locationType']
                    : modalOpenStatus['eventAddressType']
                }
                setIsOpen={setModalOpenStatus}
                filterName={
                  isCollectiveOaActive ? 'locationType' : 'eventAddressType'
                }
                handleSubmit={formik.handleSubmit}
              >
                <ModalFilterLayout
                  onClean={() =>
                    onReset(
                      isCollectiveOaActive
                        ? 'locationType'
                        : 'eventAddressType',
                      isCollectiveOaActive
                        ? CollectiveLocationType.TO_BE_DEFINED
                        : OfferAddressType.OTHER
                    )
                  }
                  onSearch={() =>
                    onSearch(
                      isCollectiveOaActive ? 'locationType' : 'eventAddressType'
                    )
                  }
                >
                  <RadioGroup
                    group={adressTypeRadios}
                    className={styles['filter-container-evenement']}
                    name={
                      isCollectiveOaActive ? 'locationType' : 'eventAddressType'
                    }
                    legend="Choisir un type d'intervention"
                    checkedOption={formik.values.eventAddressType}
                    onChange={formik.handleChange}
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
                      name="departments"
                      label="Rechercher un département"
                      options={departmentOptions}
                      isOpen={modalOpenStatus['localisation']}
                      selectedOptions={formik.values.departments}
                      onSelectedOptionsChanged={(selectedItems) =>
                        setMultiselectValue('departments', selectedItems)
                      }
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
                      name="academies"
                      label="Rechercher une académie"
                      options={academiesOptions}
                      isOpen={modalOpenStatus['localisation']}
                      selectedOptions={formik.values.academies}
                      onSelectedOptionsChanged={(selectedItems) =>
                        setMultiselectValue('academies', selectedItems)
                      }
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
                        name="geolocRadius"
                        label="Dans un rayon de"
                        scale="km"
                        min={1}
                        max={100}
                        displayValue={true}
                        onChange={formik.handleChange}
                        value={formik.values.geolocRadius}
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
                    name="domains"
                    label="Rechercher un domaine artistique"
                    options={domainsOptions}
                    isOpen={modalOpenStatus['domains']}
                    selectedOptions={formik.values.domains}
                    onSelectedOptionsChanged={(selectedItems) =>
                      setMultiselectValue('domains', selectedItems)
                    }
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
                    name="formats"
                    label="Rechercher un format"
                    options={formatsOptions}
                    isOpen={modalOpenStatus['formats']}
                    selectedOptions={formik.values.formats}
                    onSelectedOptionsChanged={(selectedItems) =>
                      setMultiselectValue('formats', selectedItems)
                    }
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
                  title="Choisir un niveau scolaire"
                >
                  <AdageMultiselect
                    name="students"
                    label="Rechercher un niveau scolaire"
                    options={studentsOptionsFiltered}
                    isOpen={modalOpenStatus['students']}
                    selectedOptions={formik.values.students}
                    onSelectedOptionsChanged={(selectedItems) =>
                      setMultiselectValue('students', selectedItems)
                    }
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
