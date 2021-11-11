/*
* @debt complexity "Gaël: file nested too deep in directory structure"
*/

import getLabelFromList from '../getLabelFromList'

describe('getLabelFromList', () => {
  it('should return "-" when no id matches', () => {
    // given
    const list = [
      {
        id: 'DA',
        label: "Centre d'art et d'essais",
      },
      {
        id: 'BA',
        label: 'Jeux vidéo',
      },
    ]
    const searchingId = 'AE'

    // when
    const result = getLabelFromList(list, searchingId)

    // then
    expect(result).toStrictEqual('-')
  })
  it('should return the matching label when id matches', () => {
    // give
    const list = [
      {
        id: 'DA',
        label: "Centre d'art et d'essais",
      },
      {
        id: 'BA',
        label: 'Jeux vidéo',
      },
    ]
    const searchingId = 'DA'

    // when
    const result = getLabelFromList(list, searchingId)

    // then
    expect(result).toStrictEqual("Centre d'art et d'essais")
  })
})
