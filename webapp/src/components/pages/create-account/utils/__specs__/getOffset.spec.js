import { getOffset } from '../getOffset'

describe('should return proper offset based on timezone', () => {
  const getTimezoneOffset = Date.prototype.getTimezoneOffset

  afterEach(() => {
    Date.prototype.getTimezoneOffset = getTimezoneOffset
  })

  it('should return +02:00 when tz is Europe/Paris', () => {
    // given
    Date.prototype.getTimezoneOffset = () => -120

    // when
    const offset = getOffset()

    // then
    expect(offset).toBe('+02:00')
  })

  it('should return -01:00 when tz is America/Scoresbysund', () => {
    // given
    Date.prototype.getTimezoneOffset = () => +60

    // when
    const offset = getOffset()

    // then
    expect(offset).toBe('-01:00')
  })

  it('should return -11:00 when tz is Pacific/Niue', () => {
    // given
    Date.prototype.getTimezoneOffset = () => +660

    // when
    const offset = getOffset()

    // then
    expect(offset).toBe('-11:00')
  })

  it('should return +10 when tz is Asia/Vladivostok', () => {
    // given
    Date.prototype.getTimezoneOffset = () => -600

    // when
    const offset = getOffset()

    // then
    expect(offset).toBe('+10:00')
  })

  it('should return +00:00 when tz is Africa/Nouakchott', () => {
    // given
    Date.prototype.getTimezoneOffset = () => 0

    // when
    const offset = getOffset()

    // then
    expect(offset).toBe('+00:00')
  })

  it('should return +09:00 when tz is Asia/Pyongyang', () => {
    // given
    Date.prototype.getTimezoneOffset = () => -540

    // when
    const offset = getOffset()

    // then
    expect(offset).toBe('+09:00')
  })
})
