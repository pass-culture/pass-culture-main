import type { FormikErrors } from 'formik'

import {
  ALL_FRANCE_OPTION_VALUE,
  MAINLAND_OPTION_VALUE,
  allDepartmentValues,
  mainlandValues,
} from 'core/Venue'

import { CollectiveDataFormValues } from '../type'

const areAllMainlandDepartmentsSelected = (formikValues: string[]) =>
  mainlandValues.every(departmentValue =>
    formikValues.includes(departmentValue)
  )

export const areAllDepartmentsSelected = (formikValues: string[]) =>
  allDepartmentValues.every(departmentValue =>
    formikValues.includes(departmentValue)
  )

export const handleAllFranceDepartmentOptions = (
  formikValues: string[],
  previousFormikValues: string[] | null,
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => Promise<void> | Promise<FormikErrors<CollectiveDataFormValues>>
) => {
  let allDepartmentsSelected = areAllDepartmentsSelected(formikValues)
  let allMainlandDepartmentsSelected =
    allDepartmentsSelected || areAllMainlandDepartmentsSelected(formikValues)

  // a user can only deselect "Toute la France" if all departments are checked
  const userUnselectedAllFrance =
    previousFormikValues?.includes(ALL_FRANCE_OPTION_VALUE) &&
    !formikValues.includes(ALL_FRANCE_OPTION_VALUE) &&
    allDepartmentsSelected

  // a user can only deselect "France métropolitaine" if all mainland departments are checked
  const userUnselectedMainland =
    previousFormikValues?.includes(MAINLAND_OPTION_VALUE) &&
    !formikValues.includes(MAINLAND_OPTION_VALUE) &&
    allMainlandDepartmentsSelected

  if (userUnselectedAllFrance) {
    return setFieldValue(
      'collectiveInterventionArea',
      formikValues.filter(
        value =>
          !allDepartmentValues.includes(value) &&
          value !== MAINLAND_OPTION_VALUE
      )
    )
  }

  if (userUnselectedMainland) {
    return setFieldValue(
      'collectiveInterventionArea',
      formikValues.filter(
        value =>
          !(mainlandValues.includes(value) || value == ALL_FRANCE_OPTION_VALUE)
      )
    )
  }

  const userSelectedAllFrance =
    !previousFormikValues?.includes(ALL_FRANCE_OPTION_VALUE) &&
    formikValues.includes(ALL_FRANCE_OPTION_VALUE)

  const userSelectedMainland =
    !previousFormikValues?.includes(MAINLAND_OPTION_VALUE) &&
    formikValues.includes(MAINLAND_OPTION_VALUE)

  let newValues = new Set(formikValues)

  if (userSelectedAllFrance) {
    newValues = new Set([
      ...formikValues,
      ...allDepartmentValues,
      MAINLAND_OPTION_VALUE,
    ])
  }

  if (userSelectedMainland) {
    newValues = new Set([...formikValues, ...mainlandValues])
  }

  allDepartmentsSelected = areAllDepartmentsSelected([...newValues])
  allMainlandDepartmentsSelected =
    allDepartmentsSelected || areAllMainlandDepartmentsSelected([...newValues])

  if (allMainlandDepartmentsSelected) {
    newValues.add(MAINLAND_OPTION_VALUE)
  }

  if (newValues.has(MAINLAND_OPTION_VALUE) && !allMainlandDepartmentsSelected) {
    newValues.delete(MAINLAND_OPTION_VALUE)
  }

  if (allDepartmentsSelected) {
    newValues.add(ALL_FRANCE_OPTION_VALUE)
  }

  if (newValues.has(ALL_FRANCE_OPTION_VALUE) && !allDepartmentsSelected) {
    newValues.delete(ALL_FRANCE_OPTION_VALUE)
  }

  // This is to avoid infinite loop as formik values are immutable
  if (newValues.size !== formikValues.length) {
    return setFieldValue('collectiveInterventionArea', [...newValues])
  }

  return
}
