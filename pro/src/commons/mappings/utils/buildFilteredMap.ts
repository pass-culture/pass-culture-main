export function buildFilteredMap(
  enumObject: Record<string, string>,
  mappingsObject: Record<string, string>
) {
  // Checks if keys between backend model and frontend mappings are exactly the same (it will throw if not)
  ensureMappingsMatch(enumObject, mappingsObject)

  return Identity(mappingsObject)
    .map(Object.entries)
    .map(sortEntriesByValue('fr-FR'))
    .map(putKeyAtTheEnd('OTHER'))
    .fold(Object.fromEntries)
}

/**
 * Internal utils functions
 */

function ensureMappingsMatch(
  backEndKeysObject: Record<string, string>,
  frontEndKeysObject: Record<string, string>
): void {
  const backEndKeys = new Set(Object.keys(backEndKeysObject))
  const frontEndKeys = new Set(Object.keys(frontEndKeysObject))

  const difference = backEndKeys.symmetricDifference(frontEndKeys)

  const backEndExtraKeys = backEndKeys.difference(frontEndKeys)
  const frontEndExtraKeys = frontEndKeys.difference(backEndKeys)

  if (difference.size > 0) {
    throw new Error(
      `[OnboardingActivity Mapper] Mismatch keys between back-end and front-end:\n` +
        (backEndExtraKeys.size > 0
          ? `- Following keys are present in OnboardingActivity model, but not in the mappings list:\n\t${Array.from(backEndExtraKeys.keys()).join(',')}\n`
          : '') +
        (frontEndExtraKeys.size > 0
          ? `- Following keys are present in the mappings list, but not in the OnboardingActivity model:\n\t${Array.from(frontEndExtraKeys.keys()).join(',')}\n`
          : '')
    )
  }
}

type Entries = [string, string][]

function Identity<T>(val: T) {
  return {
    map: <U>(fn: (val: T) => U) => Identity<U>(fn(val)),
    fold: <U>(fn: (val: T) => U) => fn(val),
  }
}

function sortEntriesByValue(locale: string): (val: Entries) => Entries {
  const compareFn = new Intl.Collator(locale).compare
  return (val: Entries): Entries => {
    return val.toSorted((a, b) => compareFn(a[1], b[1]))
  }
}

function putKeyAtTheEnd(key: string): (val: Entries) => Entries {
  return (val: Entries): Entries => {
    const otherIndex = val.findIndex(([k]) => k === key)
    const other = val[otherIndex]
    return otherIndex > -1 ? val.toSpliced(otherIndex, 1).concat([other]) : val
  }
}
