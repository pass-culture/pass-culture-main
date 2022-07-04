import {
  ALL_FRANCE_OPTION_VALUE,
  MAINLAND_OPTION_VALUE,
  allDepartmentValues,
  mainlandValues,
} from '../interventionOptions'

import { CollectiveDataFormValues } from '../type'
import type { FormikErrors } from 'formik'

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
  const allDepartmentsSelected = areAllDepartmentsSelected(formikValues)
  const allMainlandDepartmentsSelected =
    allDepartmentsSelected || areAllMainlandDepartmentsSelected(formikValues)

  // values does not include "Toute la France" and all departments are selected
  // Case 1 : user unselected the option --> we need to unselect all departments options
  // Case 2 : user selected the last department option --> we need to select "Toute la France"
  if (
    allDepartmentsSelected &&
    !formikValues.includes(ALL_FRANCE_OPTION_VALUE)
  ) {
    // Unselect all departments + "France métropolitaine" if user has unselected "Toute la France"
    if (
      previousFormikValues &&
      previousFormikValues.includes(ALL_FRANCE_OPTION_VALUE)
    ) {
      setFieldValue(
        'collectiveInterventionArea',
        formikValues.filter(
          value =>
            !allDepartmentValues.includes(value) &&
            value !== MAINLAND_OPTION_VALUE
        )
      )
    } else {
      // Select "Toute la France" + "France métropolitaine" if user has selected all departements
      setFieldValue('collectiveInterventionArea', [
        ...new Set([
          ...formikValues,
          ALL_FRANCE_OPTION_VALUE,
          MAINLAND_OPTION_VALUE,
        ]),
      ])
    }
  }

  // values includes "Toute la France" but not all departments
  // Case 1 : user unselected one department --> we need to unselect "Toute la France"
  // Case 2 : user selected "Toute la France" --> we need to select all departments
  else if (
    formikValues.includes(ALL_FRANCE_OPTION_VALUE) &&
    !allDepartmentsSelected
  ) {
    // Unselect "Toute la France" if user has unselected a department but all were selected before
    if (
      previousFormikValues &&
      areAllDepartmentsSelected(previousFormikValues)
    ) {
      setFieldValue(
        'collectiveInterventionArea',
        formikValues.filter(value => {
          // If user has unselected a mainland department option we also need to unselect "France métropolitaine"
          if (!allMainlandDepartmentsSelected) {
            return (
              value !== ALL_FRANCE_OPTION_VALUE &&
              value !== MAINLAND_OPTION_VALUE
            )
          }

          // else if user has unselected un domtom department option, we only unselect "Toute la France"
          return value !== ALL_FRANCE_OPTION_VALUE
        })
      )
    } else {
      // Select all departments + "France métropolitaine" if user has selected "Toute la France"
      setFieldValue('collectiveInterventionArea', [
        ...new Set([
          ...formikValues,
          ...allDepartmentValues,
          MAINLAND_OPTION_VALUE,
        ]),
      ])
    }
  }

  // values does not include "France métropolitaine" but all mainland departments are selected
  // Case 1 : user unselected an option --> we need to unselect "Toute la France" + all mainland departments
  // Case 2 : user selected the last mainland department option --> we need to select "France métropolitaine"
  else if (
    !formikValues.includes(MAINLAND_OPTION_VALUE) &&
    allMainlandDepartmentsSelected
  ) {
    // Unselect all mainland values and "Toute la France"
    if (
      previousFormikValues &&
      previousFormikValues.includes(MAINLAND_OPTION_VALUE)
    ) {
      setFieldValue(
        'collectiveInterventionArea',
        formikValues.filter(
          value =>
            value !== ALL_FRANCE_OPTION_VALUE && !mainlandValues.includes(value)
        )
      )
    } else {
      // Select "France métropolitaine"
      setFieldValue('collectiveInterventionArea', [
        ...new Set([...formikValues, MAINLAND_OPTION_VALUE]),
      ])
    }
  }

  // values includes "France métropolitaine" but not all mainland department options
  // Case 1 : user selected "France métropolitaine" --> we need to select all mainland department options
  // Case 2 : user unselected one mainland department option --> we need to unselect "France métropolitaine"
  else if (
    formikValues.includes(MAINLAND_OPTION_VALUE) &&
    !allMainlandDepartmentsSelected
  ) {
    // Select all mainland values
    if (
      previousFormikValues &&
      !previousFormikValues.includes(MAINLAND_OPTION_VALUE)
    ) {
      setFieldValue('collectiveInterventionArea', [
        ...new Set([...formikValues, ...mainlandValues]),
      ])
    } else {
      // Unselect "France métropolitaine"
      setFieldValue(
        'collectiveInterventionArea',
        formikValues.filter(value => value !== MAINLAND_OPTION_VALUE)
      )
    }
  }
}
