import { configureTestStore } from '@/commons/store/testUtils'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import { unsetSelectedAdminOfferer } from '../unsetSelectedAdminOfferer'

describe('unsetSelectedAdminOfferer', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should clear the selected admin offerer in the state and remove its local storage key', () => {
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID, '100')

    const store = configureTestStore({
      user: {
        selectedAdminOfferer: {
          ...defaultGetOffererResponseModel,
          id: 100,
        },
      },
    })

    store.dispatch(unsetSelectedAdminOfferer())

    const state = store.getState()
    expect(state.user.selectedAdminOfferer).toBeNull()
    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
    ).toBeNull()
  })
})
