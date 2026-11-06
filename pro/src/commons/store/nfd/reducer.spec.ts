import { FormatEnum, NatureEnum } from '@/apiClient/v1'
import { createStore } from '@/commons/store/store'

import { setFormat, setNature } from './reducer'

describe('NFD store', () => {
  it('should keep the selection in the store', () => {
    const { store } = createStore()
    store.dispatch(setNature(NatureEnum.BIEN))
    store.dispatch(setFormat(FormatEnum.LIVRE_PAPIER))

    expect(store.getState().nfd).toEqual({
      nature: NatureEnum.BIEN,
      format: FormatEnum.LIVRE_PAPIER,
    })
  })

  it('should start with an empty selection in a new store', () => {
    const { store } = createStore()
    expect(store.getState().nfd).toEqual({})
  })
})
