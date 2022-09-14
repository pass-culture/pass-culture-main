import { findLastIndex } from '../findLastIndex'

describe('findLastIndex', () => {
  it('should return last index when it satisfies the condition', () => {
    // given
    const testArray = [
      { index: 0, isTrue: true },
      { index: 1, isTrue: true },
      { index: 2, isTrue: true },
      { index: 3, isTrue: true },
    ]
    const anotherArray = [
      { index: 0, isTrue: true },
      { index: 1, isTrue: true },
      { index: 2, isTrue: false },
      { index: 3, isTrue: false },
    ]

    // when
    const expectedIndex = findLastIndex(testArray, elem => elem.isTrue)
    const anotherExpectedIndex = findLastIndex(
      anotherArray,
      elem => elem.isTrue
    )

    // then
    expect(expectedIndex).toBe(testArray[3].index)
    expect(anotherExpectedIndex).toBe(anotherArray[1].index)
  })

  it('should return -1 when no element satisfies the condition', () => {
    // given
    const testArray = [
      { id: 0, isTrue: false },
      { id: 1, isTrue: false },
      { id: 2, isTrue: false },
      { id: 3, isTrue: false },
    ]

    // when
    const expectedIndex = findLastIndex(testArray, elem => elem.isTrue)

    // then
    expect(expectedIndex).toBe(-1)
  })
})
