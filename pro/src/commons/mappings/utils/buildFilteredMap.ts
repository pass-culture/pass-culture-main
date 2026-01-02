export function buildFilteredMap(
  enumObject: Record<string, string>,
  mappingsObject: Record<string, string>,
  enumObjectTypeName: string
) {
  // Checks if keys between backend model and frontend mappings are exactly the same (it will throw if not)
  ensureMappingsMatch(enumObject, mappingsObject, enumObjectTypeName)

  const entries = Object.entries(mappingsObject)
  const sortedEntries = sortEntriesByValue('fr-FR')(entries)
  const finalEntries = putKeyAtTheEnd('OTHER')(sortedEntries)
  return Object.fromEntries(finalEntries)
}

/**
 * Internal utils functions
 */

function ensureMappingsMatch(
  backEndKeysObject: Record<string, string>,
  frontEndKeysObject: Record<string, string>,
  backEndKeysTypeName: string
): void {
  const backEndKeys = new Set(Object.keys(backEndKeysObject))
  const frontEndKeys = new Set(Object.keys(frontEndKeysObject))

  const diff = symmetricDifference(backEndKeys, frontEndKeys)

  const backEndExtraKeys = difference(backEndKeys, frontEndKeys)
  const frontEndExtraKeys = difference(frontEndKeys, backEndKeys)

  if (diff.size > 0) {
    throw new Error(
      `[${backEndKeysTypeName} Mapper] Mismatch keys between back-end and front-end:\n` +
        (backEndExtraKeys.size > 0
          ? `- Following keys are present in ${backEndKeysTypeName} model, but not in the mappings list:\n\t${Array.from(backEndExtraKeys.keys()).join(',')}\n`
          : '') +
        (frontEndExtraKeys.size > 0
          ? `- Following keys are present in the mappings list, but not in the ${backEndKeysTypeName} model:\n\t${Array.from(frontEndExtraKeys.keys()).join(',')}\n`
          : '')
    )
  }
}

type Entries = [string, string][]

function sortEntriesByValue(locale: string): (val: Entries) => Entries {
  const compareFn = new Intl.Collator(locale).compare
  return (val: Entries): Entries => {
    const valCopy: Entries = [...val]
    return valCopy.sort((a, b) => compareFn(a[1], b[1]))
  }
}

function putKeyAtTheEnd(key: string): (val: Entries) => Entries {
  return (val: Entries): Entries => {
    const otherIndex = val.findIndex(([k]) => k === key)
    const other = val[otherIndex]
    const valCopy: Entries = [...val]
    if (otherIndex > -1) {
      valCopy.splice(otherIndex, 1)
      return valCopy.concat([other])
    }
    return val
  }
}

// TODO (jclery, 2025-11-25):
//  Can be removed once support of `Set.prototype.symmetricDifference` and `Set.prototype.difference` both fit with our own supports rules.
function symmetricDifference(setA: Set<string>, setB: Set<string>) {
  return new Set([...setA, ...setB].filter((x) => !setA.has(x) || !setB.has(x)))
}

function difference(setA: Set<string>, setB: Set<string>) {
  return new Set([...setA].filter((x) => !setB.has(x)))
}
