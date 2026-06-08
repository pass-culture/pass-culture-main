import { getMapKeys, toSelectOptions } from '../helpers'

const testMap: ReadonlyMap<string, string> = new Map([
  ['ALPHA', 'Lettre alpha'],
  ['BRAVO', 'Lettre bravo'],
  ['CHARLIE', 'Lettre charlie'],
])

describe('getMapKeys', () => {
  it('should return all keys of the map as an array', () => {
    expect(getMapKeys(testMap)).toEqual(['ALPHA', 'BRAVO', 'CHARLIE'])
  })

  it('should return an empty array for an empty map', () => {
    expect(getMapKeys(new Map())).toEqual([])
  })
})

describe('toSelectOptions', () => {
  it('should transform map entries into { label, value } objects', () => {
    expect(toSelectOptions(testMap)).toEqual([
      { label: 'Lettre alpha', value: 'ALPHA' },
      { label: 'Lettre bravo', value: 'BRAVO' },
      { label: 'Lettre charlie', value: 'CHARLIE' },
    ])
  })

  it('should return an empty array for an empty map', () => {
    expect(toSelectOptions(new Map())).toEqual([])
  })
})
