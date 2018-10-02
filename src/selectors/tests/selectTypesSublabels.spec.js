import selectTypeSublabelsSelector from '../selectTypeSublabels'
import state from './mocks/state'

describe('selectTypeSublabelsSelector', () => {
  it('should select the global state', () => {
    expect(selectTypeSublabelsSelector(state)).toEqual([
      'Applaudir',
      'Jouer',
      'Lire',
      'Pratiquer',
      'Regarder',
      'Rencontrer',
      'Écouter',
    ])
  })
})
