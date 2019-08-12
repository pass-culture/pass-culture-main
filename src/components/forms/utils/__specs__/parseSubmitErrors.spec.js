import { parseSubmitErrors } from '../parseSubmitErrors'

describe('src | components | forms | utils | parseSubmitErrors ', () => {
  it('tODO Remplire ce test', () => {
    // given
    const errors = {
      identifier: ['identifiant incorrect'],
      password: ['mot de passe incorrect'],
    }

    // when
    const result = parseSubmitErrors(errors)
    const expected = {
      identifier: ['identifiant incorrect'],
      password: ['mot de passe incorrect'],
    }

    // then
    expect(result).toStrictEqual(expected)
  })
})
