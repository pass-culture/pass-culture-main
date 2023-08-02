import { RootState } from 'store/reducers'

export function maintenanceSelector(state: RootState) {
  return state.maintenance.isActivated
}
