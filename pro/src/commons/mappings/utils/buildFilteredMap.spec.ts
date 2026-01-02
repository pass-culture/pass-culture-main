import { describe, expect, it } from 'vitest'

import { buildFilteredMap } from './buildFilteredMap'

describe('buildFilteredMap', () => {
  it('should return the sorted mapping object', () => {
    enum ColorsEnum {
      RED = 'RED',
      GREEN = 'GREEN',
      BLUE = 'BLUE',
    }

    const Mappings = {
      RED: 'Rouge',
      GREEN: 'Vert',
      BLUE: 'Bleu',
    }

    const map = buildFilteredMap(ColorsEnum, Mappings, 'ColorsEnum')

    const expected = {
      BLUE: 'Bleu',
      RED: 'Rouge',
      GREEN: 'Vert',
    }

    expect(Object.entries(map)).toEqual(Object.entries(expected))
  })

  it('should return the sorted mapping object, but with OTHER at the end', () => {
    enum ColorsEnum {
      OTHER = 'OTHER',
      RED = 'RED',
      GREEN = 'GREEN',
      BLUE = 'BLUE',
    }

    const Mappings = {
      OTHER: 'Autre',
      RED: 'Rouge',
      GREEN: 'Vert',
      BLUE: 'Bleu',
    }

    const map = buildFilteredMap(ColorsEnum, Mappings, 'ColorsEnum')

    const expected = {
      BLUE: 'Bleu',
      RED: 'Rouge',
      GREEN: 'Vert',
      OTHER: 'Autre',
    }

    expect(Object.entries(map)).toEqual(Object.entries(expected))
  })

  it("should throw if keys in the Enum and the Mapping object doesn't exactly match", () => {
    enum ColorsEnum {
      RED = 'RED',
      GREEN = 'GREEN',
      BLUE = 'BLUE',
      ORANGE = 'ORANGE',
    }

    const Mappings = {
      RED: 'Rouge',
      GREEN: 'Vert',
      BLUE: 'Bleu',
    }

    const expectedErrorMessage =
      '[ColorsEnum Mapper] Mismatch keys between back-end and front-end:\n' +
      '- Following keys are present in ColorsEnum model, but not in the mappings list:\n' +
      '\tORANGE'

    expect(() => buildFilteredMap(ColorsEnum, Mappings, 'ColorsEnum')).toThrow(
      expectedErrorMessage
    )
  })
})
