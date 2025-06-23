import { useFormContext } from 'react-hook-form'

import { OfferAddressType } from 'apiClient/adage'
import { CollectiveLocationType } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import fullClearIcon from 'icons/full-clear.svg'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { departmentOptions } from 'pages/AdageIframe/app/constants/departmentOptions'
import { Option } from 'pages/AdageIframe/app/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { SearchFormValues } from '../../OffersInstantSearch'
import { areFiltersEmpty } from '../../utils'
import { LocalisationFilterStates } from '../OffersSearch'

import styles from './FiltersTags.module.scss'

interface FiltersTagsProps {
  domainsOptions: Option<number>[]
  localisationFilterState: LocalisationFilterStates
  setLocalisationFilterState: (state: LocalisationFilterStates) => void
  resetForm: () => void
  onSubmit: () => void
  setIsUserTriggered?: (isUserTriggered: boolean) => void
}

const createTag = (label: string, onClose: () => void) => {
  if (!label) {
    return null
  }
  return (
    <button
      className={styles['adage-tag']}
      onClick={() => onClose()}
      type="button"
      key={label}
    >
      {label}
      <SvgIcon
        className={styles['adage-tag-icon']}
        src={fullClearIcon}
        alt={`Supprimer ${label}`}
        width={'20'}
      />
    </button>
  )
}

export const FiltersTags = ({
  domainsOptions,
  localisationFilterState,
  setLocalisationFilterState,
  resetForm,
  onSubmit,
  setIsUserTriggered,
}: FiltersTagsProps) => {
  const form = useFormContext<SearchFormValues>()

  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const getOfferAdressTypeTag = () => {
    const eventAddressTypeValue = form.watch('eventAddressType')
    const locationTypeValue = form.watch('locationType')
    if (
      eventAddressTypeValue === OfferAddressType.OTHER &&
      locationTypeValue === CollectiveLocationType.TO_BE_DEFINED
    ) {
      return <></>
    }

    const label =
      eventAddressTypeValue === OfferAddressType.OFFERER_VENUE ||
      locationTypeValue === CollectiveLocationType.ADDRESS
        ? 'Sortie chez un partenaire culturel'
        : 'Intervention d’un partenaire culturel dans mon établissement'

    return createTag(label, () => {
      if (isCollectiveOaActive) {
        form.setValue('locationType', CollectiveLocationType.TO_BE_DEFINED)
      } else {
        form.setValue('eventAddressType', OfferAddressType.OTHER)
      }
      onSubmit()
    })
  }
  const getGeoLocalisationTag = () => {
    if (localisationFilterState !== LocalisationFilterStates.GEOLOCATION) {
      return null
    }
    return createTag(
      `Localisation des partenaires : < à ${form.watch('geolocRadius')} km`,
      () => {
        form.setValue('geolocRadius', 50)
        setLocalisationFilterState(LocalisationFilterStates.NONE)
        setIsUserTriggered && setIsUserTriggered(true)
      }
    )
  }

  const getVenueTag = () => {
    const venueValue = form.watch('venue')
    if (!venueValue) {
      return null
    }
    const venueDisplayName = `Lieu :  ${
      venueValue.publicName || venueValue.name
    }`
    return createTag(venueDisplayName, () => {
      form.setValue('venue', null)
      onSubmit()
    })
  }

  const academiesValue = form.watch('academies')
  const departmentsValue = form.watch('departments')
  const domainsValue = form.watch('domains')
  const studentsValue = form.watch('students')
  const formatsValue = form.watch('formats')
  return (
    <div className={styles.container}>
      {getVenueTag()}
      {getOfferAdressTypeTag()}
      {getGeoLocalisationTag()}
      {academiesValue.map((academy) =>
        createTag(academy, () => {
          const updatedAcademies = academiesValue.filter((x) => x !== academy)
          form.setValue('academies', updatedAcademies)
          if (updatedAcademies.length === 0) {
            setLocalisationFilterState(LocalisationFilterStates.NONE)
            setIsUserTriggered && setIsUserTriggered(true)
          } else {
            onSubmit()
          }
        })
      )}
      {departmentsValue.map((department) =>
        createTag(
          departmentOptions.find((dpt) => dpt.value === department)?.label ||
            '',
          () => {
            const updatedDepartments = departmentsValue.filter(
              (x) => x !== department
            )
            form.setValue('departments', updatedDepartments)
            if (updatedDepartments.length === 0) {
              setLocalisationFilterState(LocalisationFilterStates.NONE)
              setIsUserTriggered && setIsUserTriggered(true)
            } else {
              onSubmit()
            }
          }
        )
      )}
      {domainsValue.map((domain) =>
        createTag(
          domainsOptions.find((dmn) => dmn.value === Number(domain))?.label ||
            '',
          () => {
            form.setValue(
              'domains',
              domainsValue.filter((x) => x !== domain)
            )
            onSubmit()
          }
        )
      )}
      {studentsValue.map((student) =>
        createTag(student, () => {
          form.setValue(
            'students',
            studentsValue.filter((x) => x !== student)
          )
          onSubmit()
        })
      )}

      {formatsValue.map((format) =>
        createTag(format, () => {
          form.setValue(
            'formats',
            formatsValue.filter((x) => x !== format)
          )
          onSubmit()
        })
      )}
      {!areFiltersEmpty(form.watch(), isCollectiveOaActive) && (
        <Button
          onClick={resetForm}
          icon={fullRefreshIcon}
          variant={ButtonVariant.TERNARY}
          type="submit"
        >
          Réinitialiser les filtres
        </Button>
      )}
    </div>
  )
}
