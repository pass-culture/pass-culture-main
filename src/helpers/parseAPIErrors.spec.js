/* eslint no-console: 0, max-nested-callbacks: 0 */
import { parseAPIErrors } from './parseAPIErrors'

describe('parseAPIErrors', () => {
  it('return empty array is empty', () => {
    const expected = []
    let values = ''
    let result = parseAPIErrors(values)
    expect(result).toEqual(expected)
    values = null
    result = parseAPIErrors(values)
    expect(result).toEqual(expected)
    // [{global: "Erreur serveur. Tentez de rafraîchir la page"}]
  })
})
