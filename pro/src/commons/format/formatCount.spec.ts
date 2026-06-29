import { formatCount } from './formatCount'

describe('formatCount', () => {
  it.each([
    { count: 0, expected: '0' },
    { count: 12, expected: '12' },
    { count: 999, expected: '999' },
    { count: 1000, expected: '1 k' },
    { count: 1499, expected: '1,5 k' },
    { count: 1500, expected: '1,5 k' },
    { count: 1999, expected: '2 k' },
    { count: 2501, expected: '2,5 k' },
    { count: 10002501, expected: '10\u202F002,5 k' },
  ])('should format $count as $expected', ({ count, expected }) => {
    expect(formatCount(count)).toBe(expected)
  })
})
