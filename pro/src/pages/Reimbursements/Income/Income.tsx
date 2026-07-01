import { useForm } from 'react-hook-form'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { noop } from '@/commons/utils/noop'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'

import styles from './Income.module.scss'
import { IncomeData } from './IncomeData/IncomeData'
import { IncomeNoData } from './IncomeNoData/IncomeNoData'

type Option = {
  id: string
  label: string
}

type VenueFormValues = {
  selectedVenues: Option[]
}

const Income = () => {
  const venues = useAppSelector((state) => state.user.venues)
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  const venueValues = (venues ?? [])
    .filter((venue) => venue.managingOffererId === selectedAdminOfferer?.id)
    .map((venue) => ({
      id: String(venue.id),
      label: venue.publicName,
    }))
    .sort((a, b) =>
      a.label.localeCompare(b.label, 'fr', { sensitivity: 'base' })
    )

  const form = useForm<VenueFormValues>({
    values: { selectedVenues: venueValues },
  })

  const {
    register,
    watch,
    setValue,
    setError,
    clearErrors,
    formState: { errors },
  } = form

  const selected = watch('selectedVenues').map((v) => v.id)

  const hasVenues = venueValues.length > 0
  const hasSingleVenue = venueValues.length === 1

  const onChange = (options: Option[]) => {
    if (options.length === 0) {
      setError('selectedVenues', {
        message: 'Vous devez sélectionner au moins un partenaire',
      })
    } else {
      clearErrors('selectedVenues')
    }

    setTimeout(() => setValue('selectedVenues', options), 1000)
  }

  if (!hasVenues) {
    return <IncomeNoData type="venues" />
  }

  return (
    <>
      {!hasSingleVenue && (
        <>
          <FormLayout.MandatoryInfo />
          <div className={styles['income-filters']}>
            <MultiSelect
              {...register('selectedVenues', { minLength: 1 })}
              required={true}
              buttonLabel="Partenaire(s) sélectionné(s)"
              className={styles['income-input']}
              label="Partenaire(s) sélectionné(s)"
              options={venueValues}
              defaultOptions={venueValues}
              hasSearch
              searchLabel="Rechercher un partenaire"
              onSelectedOptionsChanged={(selectedOption) =>
                onChange(selectedOption)
              }
              error={errors.selectedVenues?.message}
              onBlur={() => noop}
            />
          </div>
        </>
      )}

      <IncomeData
        selected={selected}
        hasSingleVenue={hasSingleVenue}
        selectedAdminOfferer={selectedAdminOfferer}
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Income
