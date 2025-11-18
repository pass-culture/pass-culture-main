import { buildSelectOptions } from '../buildSelectOptions'

const ColorsObject = {
  RED: 'Rouge',
  GREEN: 'Vert',
  BLUE: 'Bleu',
}

describe('buildSelectOptions', () => {
  it('should build select options from an object records', () => {
    const options = buildSelectOptions(ColorsObject)
    expect(options).toEqual([
      { label: 'Rouge', value: 'RED' },
      { label: 'Vert', value: 'GREEN' },
      { label: 'Bleu', value: 'BLUE' },
    ])
  })
})
