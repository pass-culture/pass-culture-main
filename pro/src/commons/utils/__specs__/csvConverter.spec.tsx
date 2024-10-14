import { convertFromCsvToObject } from '../csvConverter'

describe('convertFromCsvToObject', () => {
  it('should return an object containing csv headers and data', () => {
    const csv = 'Column1;Column2\nData1;Data2\nData3;Data4'

    const result = convertFromCsvToObject(csv)

    expect(result).toStrictEqual({
      data: [
        ['Data1', 'Data2'],
        ['Data3', 'Data4'],
      ],
      headers: ['Column1', 'Column2'],
    })
  })

  it('should return an object containing csv headers and data ignoring empty lines', () => {
    const csv = 'Column1;Column2\nData1;Data2\nData3;Data4\n'

    const result = convertFromCsvToObject(csv)

    expect(result).toStrictEqual({
      data: [
        ['Data1', 'Data2'],
        ['Data3', 'Data4'],
      ],
      headers: ['Column1', 'Column2'],
    })
  })

  it('should ignore quotes of quoted column', () => {
    const csv = 'Column1;Column2\nData1;"Data2"\nData3;"Data4"\n'

    const result = convertFromCsvToObject(csv)

    expect(result).toStrictEqual({
      data: [
        ['Data1', 'Data2'],
        ['Data3', 'Data4'],
      ],
      headers: ['Column1', 'Column2'],
    })
  })

  it('should ignore delimiter when inside quoted column', () => {
    const csv = 'Column1;Column2\nData1;"Data;2"\nData3;"Data;4"\n'

    const result = convertFromCsvToObject(csv)

    expect(result).toStrictEqual({
      data: [
        ['Data1', 'Data;2'],
        ['Data3', 'Data;4'],
      ],
      headers: ['Column1', 'Column2'],
    })
  })

  it('should keep quotes when not quoting a column', () => {
    const csv =
      'Column1;Column2\n"Data with some ""quotes"" 1";Data2\n"Other data with ""quotes""";Data4\n'

    const result = convertFromCsvToObject(csv)

    expect(result).toStrictEqual({
      data: [
        ['Data with some "quotes" 1', 'Data2'],
        ['Other data with "quotes"', 'Data4'],
      ],
      headers: ['Column1', 'Column2'],
    })
  })
})
