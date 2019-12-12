export function isMaintenanceSelector(state) {
  return state.maintenance.isActivated
}

export default isMaintenanceSelector
