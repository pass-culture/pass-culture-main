import getDepartementByCode from '../../../../utils/getDepartementByCode'

export const getDepartment = departmentCode => {
  const departmentName = getDepartementByCode(departmentCode)
  return `${departmentName} (${departmentCode})`
}
