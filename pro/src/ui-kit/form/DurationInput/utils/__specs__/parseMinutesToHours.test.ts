import { parseMinutesToHours } from '../parseMinutesToHours'

describe('parseMinutesToHours', () => {
  it('should format value', () => {
    expect(parseMinutesToHours(62)).toStrictEqual('1:02')
  })

  it('should return empty string', () => {
    expect(parseMinutesToHours(0)).toStrictEqual('')
  })
})
