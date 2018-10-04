import selectTypeSublabelsSelector, { selectTypes } from '../selectTypes'
import state from '../../mocks/stateWithTypes'

describe('selectTypeSublabels', () => {
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
describe.skip('selectTypes', () => {
  it('should select the global state', () => {
    // TODO
    expect(selectTypes(state)).toEqual([
      {
        description:
          'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
        sublabel: 'Applaudir',
      },
      {
        description: 'Lorem Ipsum',
        sublabel: 'Jouer',
      },
      {
        description: 'Lorem Ipsum',
        sublabel: 'Lire',
      },
      {
        description: 'Lorem Ipsum',
        sublabel: 'Pratiquer',
      },
      {
        description: 'Lorem Ipsum',
        sublabel: 'Regarder',
      },
      {
        description: 'Lorem Ipsum',
        sublabel: 'Rencontrer',
      },
      {
        description: 'Lorem Ipsum',
        sublabel: 'Écouter',
      },
    ])
  })
})
