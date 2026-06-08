import { createMap } from '..'
import { putKeyAtTheEnd, sortEntriesByValue } from '../helpers'

const mockedSentry = vi.hoisted(() => {
  const setContextMock = vi.fn()
  const captureException = vi.fn()
  const withScopeMock = vi.fn(
    (cb: (scope: { setContext: typeof setContextMock }) => void) =>
      cb({ setContext: setContextMock })
  )
  return { setContextMock, captureException, withScopeMock }
})

vi.mock('@sentry/browser', () => ({
  withScope: mockedSentry.withScopeMock,
  captureException: mockedSentry.captureException,
}))

vi.mock('commons/store/store', () => ({
  rootStore: {
    getState: vi.fn(() => ({
      user: { currentUser: { isImpersonated: false } },
    })),
  },
}))

const TestEnum = { ALPHA: 'Alpha', BRAVO: 'Bravo', CHARLIE: 'Charlie' } as const

describe('createMap', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should return a Map whose entries match the mappings object', () => {
    const mappings = {
      ALPHA: 'Lettre alpha',
      BRAVO: 'Lettre bravo',
      CHARLIE: 'Lettre charlie',
    } as const
    const ResultMap = createMap(mappings, TestEnum, 'TestEnum')

    expect(ResultMap.get('ALPHA')).toBe('Lettre alpha')
    expect(ResultMap.get('BRAVO')).toBe('Lettre bravo')
    expect(ResultMap.get('CHARLIE')).toBe('Lettre charlie')
    expect(ResultMap.size).toBe(3)
  })

  it('should apply post-processing pipeline in order', () => {
    const mappings = {
      ALPHA: 'Zoulou',
      BRAVO: 'Abricot',
      CHARLIE: 'Mangue',
    } as const
    const result = createMap(mappings, TestEnum, 'TestEnum', [
      sortEntriesByValue('fr'),
      putKeyAtTheEnd('BRAVO'),
    ])

    const keys = [...result.keys()]
    expect(keys[keys.length - 1]).toBe('BRAVO')
    expect(keys.indexOf('CHARLIE')).toBeLessThan(keys.indexOf('ALPHA'))
  })
})

describe('pipeline helper functions', () => {
  describe('sortEntriesByValue', () => {
    it('should sort entries alphabetically by value', () => {
      const entries: [string, string][] = [
        ['Z', 'Zèbre'],
        ['A', 'Abricot'],
        ['E', 'Élan'],
      ]
      const sorted = sortEntriesByValue('fr')(entries)

      expect(sorted.map(([, v]) => v)).toEqual(['Abricot', 'Élan', 'Zèbre'])
    })
  })

  describe('putKeyAtTheEnd', () => {
    it('should move the matching key to the last position', () => {
      const entries: [string, string][] = [
        ['A', '1'],
        ['B', '2'],
        ['C', '3'],
      ]
      const result = putKeyAtTheEnd('A')(entries)

      expect(result[result.length - 1][0]).toBe('A')
      expect(result).toHaveLength(3)
    })

    it('should return entries unchanged when key is absent', () => {
      const entries: [string, string][] = [
        ['A', '1'],
        ['B', '2'],
      ]
      const result = putKeyAtTheEnd('X')(entries)

      expect(result).toEqual([
        ['A', '1'],
        ['B', '2'],
      ])
    })
  })
})

describe('checkAssociations (via createMap)', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should not call Sentry when keys match', () => {
    const mappings = {
      ALPHA: 'Lettre alpha',
      BRAVO: 'Lettre bravo',
      CHARLIE: 'Lettre charlie',
    }
    createMap(mappings, TestEnum, 'TestEnum')

    expect(mockedSentry.captureException).not.toHaveBeenCalled()
  })

  it('should report extra back-end keys to Sentry', () => {
    const partialMappings = { ALPHA: 'Alpha', BRAVO: 'Bravo' } as Record<
      string,
      string
    >
    // @ts-expect-error - we want to test the error case
    createMap(partialMappings, TestEnum, 'SubcategoryId')

    expect(mockedSentry.captureException).toHaveBeenCalledOnce()
    const error = mockedSentry.captureException.mock.calls[0][0] as Error
    expect(error.message).toContain(
      'Following keys are present in SubcategoryId back-end model, but not in the front-end mappings list:\n\tCHARLIE'
    )
  })

  it('should report extra front-end keys to Sentry', () => {
    const extraMappings = {
      ALPHA: 'Lettre alpha',
      BRAVO: 'Lettre bravo',
      CHARLIE: 'Lettre charlie',
      UNKNOWN_KEY: 'Unknown',
    } as Record<string, string>
    // @ts-expect-error - we want to test the error case
    createMap(extraMappings, TestEnum, 'SubcategoryId')

    expect(mockedSentry.captureException).toHaveBeenCalledOnce()
    const error = mockedSentry.captureException.mock.calls[0][0] as Error
    expect(error.message).toContain(
      'Following keys are present in the front-end mappings list, but not in the SubcategoryId back-end model:\n\tUNKNOWN_KEY'
    )
  })
})

describe('notifySentry (via checkAssociations trigger)', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should call withScope and captureException', () => {
    const partialMappings = { ALPHA: 'Lettre alpha' } as Record<string, string>
    // @ts-expect-error - we want to test the error case
    createMap(partialMappings, TestEnum, 'TestEnum')

    expect(mockedSentry.withScopeMock).toHaveBeenCalledOnce()
    expect(mockedSentry.captureException).toHaveBeenCalledOnce()
  })

  it('should set isUserImpersonated context from store', () => {
    const partialMappings = { ALPHA: 'Lettre alpha' } as Record<string, string>
    // @ts-expect-error - we want to test the error case
    createMap(partialMappings, TestEnum, 'TestEnum')

    expect(mockedSentry.setContextMock).toHaveBeenCalledWith('default', {
      isUserImpersonated: false,
    })
  })
})
