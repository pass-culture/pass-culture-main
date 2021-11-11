import { fetchSandbox } from './sandboxes'
import { createUserRole } from './roles'

const createUserRoleFromUserSandbox = async (moduleName, getterName) => {
  const { user } = await fetchSandbox(moduleName, getterName)
  return createUserRole(user)
}

export default createUserRoleFromUserSandbox
