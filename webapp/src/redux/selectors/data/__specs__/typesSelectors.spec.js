import { selectTypeSublabels, selectTypeSublabelsAndDescription } from '../typesSelectors'

describe('selectTypeSublabels', () => {
  it('should return unique sub labels when a sub label appears several times', () => {
    // given
    const state = {
      data: {
        types: [
          { sublabel: 'A' },
          { sublabel: 'B' },
          { sublabel: 'B' },
          { sublabel: 'C' },
        ]
      }
    }

    // when
    const result = selectTypeSublabels(state)

    // then
    expect(result).toStrictEqual(['A', 'B', 'C'])
  })

  it('should return unique sub labels sorted by name', () => {
    // given
    const state = {
      data: {
        types: [
          { sublabel: 'B' },
          { sublabel: 'A' },
          { sublabel: 'D' },
          { sublabel: 'C' },
        ]
      }
    }

    // when
    const result = selectTypeSublabels(state)

    // then
    expect(result).toStrictEqual(['A', 'B', 'C', 'D'])
  })
})

describe('selectTypeSublabelsAndDescription', () => {
  it('should return unique sub labels and descriptions when a sub label appears several times', () => {
    // given
    const state = {
      data: {
        types: [
          { description: 'fake description', sublabel: 'B' },
          { description: 'fake description', sublabel: 'A' },
          { description: 'fake description', sublabel: 'D' },
          { description: 'fake description', sublabel: 'C' },
          { description: 'fake description', sublabel: 'C' },
        ]
      }
    }

    // when
    const result = selectTypeSublabelsAndDescription(state)

    // then
    expect(result).toStrictEqual([
      { description: 'fake description', sublabel: 'A' },
      { description: 'fake description', sublabel: 'B' },
      { description: 'fake description', sublabel: 'C' },
      { description: 'fake description', sublabel: 'D' }
    ])
  })
})
