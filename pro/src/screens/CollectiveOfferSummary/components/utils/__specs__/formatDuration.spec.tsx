import { formatDuration } from '../formatDuration'

describe('formatDuration', () => {
  it('when it is only minutes', () => {
    expect(formatDuration(34)).toBe('34min')
  })

  it('when it is only hours', () => {
    expect(formatDuration(60)).toBe('1h')
  })

  it('when it is hours and minutes', () => {
    expect(formatDuration(90)).toBe('1h30min')
  })
})
