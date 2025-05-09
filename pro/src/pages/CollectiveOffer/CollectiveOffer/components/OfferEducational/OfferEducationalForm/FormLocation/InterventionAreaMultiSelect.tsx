import { useFormikContext } from 'formik'
import { useCallback } from 'react'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { offerInterventionOptions } from 'commons/core/shared/interventionOptions'
import { interventionAreaMultiSelect } from 'commons/utils/interventionAreaMultiSelect'
import { MultiSelect, Option } from 'ui-kit/MultiSelect/MultiSelect'

import styles from '../OfferEducationalForm.module.scss'

interface InterventionAreaMultiSelectProps {
  label: string
  disabled: boolean
}

export const InterventionAreaMultiSelect = ({
  label,
  disabled,
}: InterventionAreaMultiSelectProps): JSX.Element => {
  const { setFieldValue, values, setFieldTouched, errors, touched } =
    useFormikContext<OfferEducationalFormValues>()

  const handleInterventionAreaChange = useCallback(
    (
      selectedOption: Option[],
      addedOptions: Option[],
      removedOptions: Option[]
    ) => {
      const newSelectedOptions = interventionAreaMultiSelect({
        selectedOption,
        addedOptions,
        removedOptions,
      })
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setFieldValue('interventionArea', Array.from(newSelectedOptions))
    },
    [setFieldValue]
  )

  return (
    <MultiSelect
      label={label}
      required
      name="interventionArea"
      buttonLabel="Département(s)"
      options={offerInterventionOptions}
      selectedOptions={offerInterventionOptions.filter((op) =>
        values.interventionArea.includes(op.id)
      )}
      defaultOptions={offerInterventionOptions.filter((option) =>
        values.interventionArea.includes(option.id)
      )}
      disabled={disabled}
      hasSearch
      searchLabel="Rechercher un département"
      hasSelectAllOptions
      onSelectedOptionsChanged={handleInterventionAreaChange}
      onBlur={() => setFieldTouched('interventionArea', true)}
      error={
        touched.interventionArea && errors.interventionArea
          ? String(errors.interventionArea)
          : undefined
      }
      className={styles['intervention-area']}
    />
  )
}
