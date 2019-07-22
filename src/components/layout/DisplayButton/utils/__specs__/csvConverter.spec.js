import csvConverter from '../csvConverter'

describe('src | components | layout | DisplayButton | utils', () => {
  it('should return an object containing csv headers and data', () => {
    // given
    const csv = 'Column1;Column2\nData1;Data2\nData3;Data4'

    // when
    const result = csvConverter(csv)

    // then
    expect(result).toStrictEqual({
      data: [['Data1', 'Data2'], ['Data3', 'Data4']],
      headers: ['Column1', 'Column2'],
    })
  })

  it('should return an object containing csv headers and data ignoring empty lines', () => {
    // given
    const csv = 'Column1;Column2\nData1;Data2\nData3;Data4\n'

    // when
    const result = csvConverter(csv)

    // then
    expect(result).toStrictEqual({
      data: [['Data1', 'Data2'], ['Data3', 'Data4']],
      headers: ['Column1', 'Column2'],
    })
  })
})
