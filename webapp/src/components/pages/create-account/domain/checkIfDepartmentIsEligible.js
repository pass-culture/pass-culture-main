import { eligibleDepartments } from './eligibleDepartments'

export const DEPARTMENT_ELIGIBILITY_VALUES = {
  ELIGIBLE: 'department eligible',
  NOT_ELIGIBLE: 'department not eligible',
}

export const checkIfDepartmentIsEligible = postalCode => {
  const metropolisDepartmentCode = postalCode.substr(0, 2)
  const overseasDepartmentCode = postalCode.substr(0, 3)
  const overseasDepartments = ['971', '972', '973', '974', '976']
  const isOverseas = overseasDepartments.includes(overseasDepartmentCode)

  postalCode = isOverseas ? overseasDepartmentCode : metropolisDepartmentCode

  return eligibleDepartments.includes(postalCode)
}
