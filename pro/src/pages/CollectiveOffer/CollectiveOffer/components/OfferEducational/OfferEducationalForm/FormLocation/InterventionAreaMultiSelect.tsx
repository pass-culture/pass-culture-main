import { useCallback } from 'react'
import { useFormContext } from 'react-hook-form'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { offerInterventionOptions } from 'commons/core/shared/interventionOptions'
import { selectInterventionAreas } from 'commons/utils/selectInterventionAreas'
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
  const { setValue, watch, getFieldState } =
    useFormContext<OfferEducationalFormValues>()

  const handleInterventionAreaChange = useCallback(
    (
      selectedOption: Option[],
      addedOptions: Option[],
      removedOptions: Option[]
    ) => {
      const newSelectedOptions = selectInterventionAreas({
        selectedOption,
        addedOptions,
        removedOptions,
      })
      setValue('interventionArea', Array.from(newSelectedOptions), {
        shouldValidate: true,
      })
    },
    [setValue]
  )

  return (
    <MultiSelect
      label={label}
      required
      name="interventionArea"
      buttonLabel="Département(s)"
      options={offerInterventionOptions}
      selectedOptions={offerInterventionOptions.filter((op) =>
        watch('interventionArea')?.includes(op.id)
      )}
      defaultOptions={offerInterventionOptions.filter((option) =>
        watch('interventionArea')?.includes(option.id)
      )}
      disabled={disabled}
      hasSearch
      searchLabel="Rechercher un département"
      hasSelectAllOptions
      onSelectedOptionsChanged={handleInterventionAreaChange}
      error={getFieldState('interventionArea').error?.message}
      className={styles['intervention-area']}
    />
  )
}
