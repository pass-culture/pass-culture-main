import { FormikProvider, useFormik } from 'formik'
import { useEffect } from 'react'

import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'

import styles from './IncomeVenueSelector.module.scss'

type VenueFormValues = {
  selectedVenues: string[]
  'search-selectedVenues': string
}

type IncomeVenueSelectorProps = {
  venues: { value: string; label: string }[]
  onChange: (venues: string[]) => void
}

export const IncomeVenueSelector = ({
  venues,
  onChange,
}: IncomeVenueSelectorProps) => {
  const formik = useFormik<VenueFormValues>({
    initialValues: {
      selectedVenues: venues.map((v) => v.value),
      'search-selectedVenues': '',
    },
    onSubmit: () => {},
  })

  useEffect(() => {
    onChange(formik.values.selectedVenues)
  }, [onChange, formik.values.selectedVenues])

  return (
    <FormikProvider value={formik}>
      <SelectAutocomplete
        className={styles['income-venue-selector']}
        name="selectedVenues"
        label="Partenaires"
        options={venues}
        placeholder="Partenaires"
        multi
        isLabelHidden
      />
    </FormikProvider>
  )
}
