import { mainlandOptions } from '@/commons/core/shared/interventionOptions'
import { MAINLAND_OPTION_VALUE } from '@/pages/AdageIframe/app/constants/departmentOptions'
import { Option } from '@/ui-kit/MultiSelect/MultiSelect'

type SelectInterventionAreasParams = {
  selectedOption: Option[]
  addedOptions: Option[]
  removedOptions: Option[]
}

export const selectInterventionAreas = ({
  selectedOption,
  addedOptions,
  removedOptions,
}: SelectInterventionAreasParams) => {
  const newSelectedOptions = new Set(selectedOption.map((op) => op.id))

  if (addedOptions.map((op) => op.id).includes('mainland')) {
    //  If mainland is selected, check all mainland departments
    for (const mainlandOp of mainlandOptions) {
      newSelectedOptions.add(String(mainlandOp.id))
    }
  }

  if (removedOptions.map((op) => op.id).includes('mainland')) {
    //  If mainland is removed, uncheck all mainland departments
    for (const mainlandOp of mainlandOptions) {
      newSelectedOptions.delete(String(mainlandOp.id))
    }
  }

  if (
    removedOptions
      .map((op) => op.id)
      .some((removedOp) =>
        mainlandOptions.map((op) => op.id).includes(removedOp)
      )
  ) {
    //  If a mainland department is not selected, remove the mainland from selected options
    newSelectedOptions.delete('mainland')
  }

  if (
    !newSelectedOptions.has('mainland') &&
    mainlandOptions.every((option) => newSelectedOptions.has(option.id))
  ) {
    newSelectedOptions.add(String(MAINLAND_OPTION_VALUE))
  }

  return newSelectedOptions
}
