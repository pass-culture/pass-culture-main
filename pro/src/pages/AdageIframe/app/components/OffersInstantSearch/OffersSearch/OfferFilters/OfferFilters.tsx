import { useState } from 'react'
import { FormProvider, useFormContext } from 'react-hook-form'
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
  onSubmit: () => void
}

export const OfferFilters = ({
  className,
  localisationFilterState,
  setLocalisationFilterState,
  domainsOptions,
  shouldDisplayMarseilleStudentOptions,
  onSubmit,
}: OfferFiltersProps): JSX.Element => {
  const [modalOpenStatus, setModalOpenStatus] = useState<{
    [key: string]: boolean
  }>({})

  const form = useFormContext<SearchFormValues>()

  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const { adageUser } = useAdageUser()

  const adageUserHasValidGeoloc =
    (adageUser.lat || adageUser.lat === 0) &&
    (adageUser.lon || adageUser.lon === 0)

  const getActiveLocalisationFilterCount = () => {
    if (localisationFilterState === LocalisationFilterStates.DEPARTMENTS) {
      return form.watch('departments').length
    }
    if (localisationFilterState === LocalisationFilterStates.ACADEMIES) {
      return form.watch('academies').length
    }
    return 0
  }

  const resetLocalisationFilterState = () => {
    if (
      (localisationFilterState === LocalisationFilterStates.DEPARTMENTS &&
        form.watch('departments').length === 0) ||
      (localisationFilterState === LocalisationFilterStates.ACADEMIES &&
        form.watch('academies').length === 0)
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

  const closeModal = (modalName: string, closeModal: boolean = true) => {
    if (modalName === 'localisation') {
      setLocalisationFilterState(LocalisationFilterStates.NONE)
    }
    if (closeModal) {
      setModalOpenStatus((prevState) => ({ ...prevState, [modalName]: false }))
    }
  }

  const resetModalFilter = (
    filterName: keyof SearchFormValues,
    value: string | string[] | number
  ) => {
    clearFormFieldValue(filterName, value)
    closeModal(filterName)
  }

  const onSearch = (modalName: string) => {
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

  const clearFormFieldValue = (
    fieldName: keyof SearchFormValues,
    value: string | string[] | number
  ) => {
    form.setValue(fieldName, value, {
      shouldValidate: true,
    })
    onSubmit()
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

  const setMultiselectValue = (
    name: keyof SearchFormValues,
    value: ItemProps['value'][]
  ) => {
    form.setValue(name, value as string | number | string[])
  }

  const locationFieldKey = isCollectiveOaActive
    ? 'locationType'
    : 'eventAddressType'

  const domainsValue = form.watch('domains')
  const locationTypeValue = form.watch('locationType')
  const eventAddressTypeValue = form.watch('eventAddressType')
  const formatsValue = form.watch('formats')
  const studentsValue = form.watch('students')
  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className={className}>
        <FormLayout.Row className={styles['filter-container-buttons']}>
          <div className={styles['filter-container-buttons-list']}>
            <div className={styles['filter-container-buttons-list-items']}>
              <AdageButtonFilter
                isActive={
                  isCollectiveOaActive
                    ? locationTypeValue.length > 0 &&
                      locationTypeValue !== CollectiveLocationType.TO_BE_DEFINED
                    : eventAddressTypeValue.length > 0 &&
                      eventAddressTypeValue !== OfferAddressType.OTHER
                }
                title="Type d’intervention"
                itemsLength={
                  isCollectiveOaActive
                    ? locationTypeValue &&
                      locationTypeValue !== CollectiveLocationType.TO_BE_DEFINED
                      ? 1
                      : null
                    : eventAddressTypeValue &&
                        eventAddressTypeValue !== OfferAddressType.OTHER
                      ? 1
                      : null
                }
                isOpen={modalOpenStatus[locationFieldKey]}
                setIsOpen={setModalOpenStatus}
                filterName={locationFieldKey}
                handleSubmit={onSubmit}
              >
                <ModalFilterLayout
                  onClean={() =>
                    resetModalFilter(
                      locationFieldKey,
                      isCollectiveOaActive
                        ? CollectiveLocationType.TO_BE_DEFINED
                        : OfferAddressType.OTHER
                    )
                  }
                  onSearch={() => onSearch(locationFieldKey)}
                >
                  <RadioGroup
                    name={locationFieldKey}
                    key={form.watch(locationFieldKey)}
                    group={adressTypeRadios}
                    className={styles['filter-container-evenement']}
                    legend="Choisir un type d'intervention"
                    checkedOption={form.watch(locationFieldKey)}
                    onChange={(e) =>
                      form.setValue(locationFieldKey, e.target.value)
                    }
                    variant={'default'}
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
                  onSubmit()
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
                    onClean={() => {
                      clearFormFieldValue('departments', [])
                      closeModal('localisation', false)
                    }}
                    onSearch={() => onSearch('localisation')}
                    title="Choisir un département"
                  >
                    <AdageMultiselect
                      name="departments"
                      label="Rechercher un département"
                      options={departmentOptions}
                      isOpen={modalOpenStatus['localisation']}
                      selectedOptions={form.watch('departments')}
                      onSelectedOptionsChanged={(selectedItems) =>
                        setMultiselectValue('departments', selectedItems)
                      }
                    />
                  </ModalFilterLayout>
                )}
                {localisationFilterState ===
                  LocalisationFilterStates.ACADEMIES && (
                  <ModalFilterLayout
                    onClean={() => {
                      clearFormFieldValue('academies', [])
                      closeModal('localisation', false)
                    }}
                    onSearch={() => onSearch('localisation')}
                    title="Choisir une académie"
                  >
                    <AdageMultiselect
                      name="academies"
                      label="Rechercher une académie"
                      options={academiesOptions}
                      isOpen={modalOpenStatus['localisation']}
                      selectedOptions={form.watch('academies')}
                      onSelectedOptionsChanged={(selectedItems) =>
                        setMultiselectValue('academies', selectedItems)
                      }
                    />
                  </ModalFilterLayout>
                )}
                {localisationFilterState ===
                  LocalisationFilterStates.GEOLOCATION && (
                  <ModalFilterLayout
                    onClean={() => {
                      clearFormFieldValue('geolocRadius', 50)
                      closeModal('localisation', false)
                    }}
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
                        onChange={(e) =>
                          form.setValue('geolocRadius', Number(e.target.value))
                        }
                        value={form.watch('geolocRadius')}
                      />
                    </div>
                  </ModalFilterLayout>
                )}
              </AdageButtonFilter>
              <AdageButtonFilter
                isActive={domainsValue.length > 0}
                title="Domaine artistique"
                itemsLength={domainsValue.length}
                isOpen={modalOpenStatus['domains']}
                setIsOpen={setModalOpenStatus}
                filterName="domains"
                handleSubmit={onSubmit}
              >
                <ModalFilterLayout
                  onClean={() => resetModalFilter('domains', [])}
                  onSearch={() => onSearch('domains')}
                  title="Choisir un domaine artistique"
                >
                  <AdageMultiselect
                    name="domains"
                    label="Rechercher un domaine artistique"
                    options={domainsOptions}
                    isOpen={modalOpenStatus['domains']}
                    selectedOptions={domainsValue}
                    onSelectedOptionsChanged={(selectedItems) =>
                      setMultiselectValue('domains', selectedItems)
                    }
                  />
                </ModalFilterLayout>
              </AdageButtonFilter>

              <AdageButtonFilter
                isActive={formatsValue.length > 0}
                title="Format"
                itemsLength={formatsValue.length}
                isOpen={modalOpenStatus['formats']}
                setIsOpen={setModalOpenStatus}
                filterName="formats"
                handleSubmit={onSubmit}
              >
                <ModalFilterLayout
                  onClean={() => resetModalFilter('formats', [])}
                  onSearch={() => onSearch('formats')}
                  title="Choisir un format"
                >
                  <AdageMultiselect
                    name="formats"
                    label="Rechercher un format"
                    options={formatsOptions}
                    isOpen={modalOpenStatus['formats']}
                    selectedOptions={formatsValue}
                    onSelectedOptionsChanged={(selectedItems) =>
                      setMultiselectValue('formats', selectedItems)
                    }
                  />
                </ModalFilterLayout>
              </AdageButtonFilter>

              <AdageButtonFilter
                isActive={studentsValue.length > 0}
                title="Niveau scolaire"
                itemsLength={studentsValue.length}
                isOpen={modalOpenStatus['students']}
                setIsOpen={setModalOpenStatus}
                filterName="students"
                handleSubmit={onSubmit}
              >
                <ModalFilterLayout
                  onClean={() => resetModalFilter('students', [])}
                  onSearch={() => onSearch('students')}
                  title="Choisir un niveau scolaire"
                >
                  <AdageMultiselect
                    name="students"
                    label="Rechercher un niveau scolaire"
                    options={studentsOptionsFiltered}
                    isOpen={modalOpenStatus['students']}
                    selectedOptions={studentsValue}
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
      </form>
    </FormProvider>
  )
}
