import { removeDuplicatesObjects, sortAlphabeticallyArrayOfObjectsByProperty } from '../functions'

describe('utils | array', () => {
  it('should return an array with unique values', () => {
    // given
    const types = [
      {
        description: 'Fake description',
        sublabel: 'One Label',
      },
      {
        description: 'Fake description',
        sublabel: 'One Label',
      },
      {
        description: 'Another Fake description',
        sublabel: 'Another Label',
      },
      {
        description: 'Another Fake description',
        sublabel: 'Another Label',
      },
      {
        description: 'Another Fake description',
        sublabel: 'Another Label',
      },
    ]

    // when
    const result = removeDuplicatesObjects(types)

    // then
    expect(result).toStrictEqual([
      {
        description: 'Fake description',
        sublabel: 'One Label',
      },
      {
        description: 'Another Fake description',
        sublabel: 'Another Label',
      },
    ])
  })

  it('should return an array sorted by given property (sublabel)', () => {
    // given
    const types = [
      {
        description: 'Résoudre l’énigme d’un jeu de piste dans votre ville ?',
        sublabel: 'Jouer',
      },
      {
        description: 'Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?',
        sublabel: 'Écouter',
      },
      {
        description: 'Suivre un géant de 12 mètres dans la ville ?',
        sublabel: 'Applaudir',
      },
    ]

    // when
    const result = types.sort(sortAlphabeticallyArrayOfObjectsByProperty('sublabel'))

    // then
    expect(result).toStrictEqual([
      {
        description: 'Suivre un géant de 12 mètres dans la ville ?',
        sublabel: 'Applaudir',
      },
      {
        description: 'Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?',
        sublabel: 'Écouter',
      },
      {
        description: 'Résoudre l’énigme d’un jeu de piste dans votre ville ?',
        sublabel: 'Jouer',
      },
    ])
  })
})
