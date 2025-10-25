import {
  humanizeSiret,
  isRidetStartingWithRid7,
  isSiretStartingWithSiren,
  unhumanizeRidet,
  unhumanizeSiret,
} from '../siren'

describe('siren', () => {
  describe('humanizeSiret', () => {
    const cases = [
      { input: '', output: '' },
      { input: '100F', output: '100' },
      { input: '41816609600069', output: '418 166 096 00069' },
    ]
    cases.forEach(({ input, output }) => {
      it(`should return expected outpout for input: ${input}`, () => {
        expect(humanizeSiret(input)).toEqual(output)
      })
    })
  })

  describe('unhumanizeSiret', () => {
    const cases = [
      { input: '', output: '' },
      { input: '100F', output: '100' },
      { input: '123 456 789 01234', output: '12345678901234' },
    ]
    cases.forEach(({ input, output }) => {
      it(`should return expected outpout for input: ${input}`, () => {
        expect(unhumanizeSiret(input)).toEqual(output)
      })
    })
  })

  describe('isSiretStartingWithSiren', () => {
    const cases = [
      { siret: '123 456 789 01234', siren: '123 456 789', output: true },
      { siret: '12345678901234', siren: '123 456 789', output: true },
      { siret: '123 456 789 01234', siren: '123456789', output: true },
      { siret: '023 456 789 01234', siren: '123456789', output: false },
    ]
    cases.forEach(({ siret, siren, output }) => {
      it(`should return expected outpout for siret: ${siret} and siren: ${siren}`, () => {
        expect(isSiretStartingWithSiren(siret, siren)).toEqual(output)
      })
    })
  })

  describe('unhumanizeRidet', () => {
    const cases = [
      { input: 'NC12345', output: 'NC12345' },
      { input: '12345', output: 'NC12345' },
      { input: '012345', output: 'NC012345' },
    ]
    cases.forEach(({ input, output }) => {
      it(`should return expected outpout for input: ${input}`, () => {
        expect(unhumanizeRidet(input)).toEqual(output)
      })
    })
  })

  describe('isRidetStartingWithRid7', () => {
    const cases = [
      { siret: 'NC123 456 789 01234', siren: 'NC123 4567', output: true },
      { siret: '1234567890', siren: 'NC123 456 7', output: true },
      { siret: 'NC123 456 789 0', siren: '1234567', output: true },
      { siret: 'NC123 456 789 0XX', siren: 'NC1234567', output: true },
      { siret: 'NC0234567890XX', siren: 'NC1234567', output: false },
    ]
    cases.forEach(({ siret, siren, output }) => {
      it(`should return expected outpout for siret: ${siret} and siren: ${siren}`, () => {
        expect(isRidetStartingWithRid7(siret, siren)).toEqual(output)
      })
    })
  })
})
