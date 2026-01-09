import {
  objectEntries,
  objectFromEntries,
} from '@/pages/VenueEdition/commons/utils'

type StringRecord = Record<string, string>

export function buildFilteredMap<M extends StringRecord>(
  enumObject: StringRecord,
  mappingsObject: M,
  enumObjectTypeName: string
): Record<keyof M, string> {
  // Checks if keys between backend model and frontend mappings are exactly the same (it will throw if not)
  ensureMappingsMatch(enumObject, mappingsObject, enumObjectTypeName)

  const entries = objectEntries(mappingsObject)
  const sortedEntries = sortEntriesByValue('fr-FR')(entries)
  const finalEntries = putKeyAtTheEnd('OTHER')(sortedEntries)
  return objectFromEntries(finalEntries)
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

type Entries<K = string, V = string> = [K, V][]

function sortEntriesByValue(locale: string) {
  const compareFn = new Intl.Collator(locale).compare
  return <K, V extends string>(val: Entries<K, V>): Entries<K, V> => {
    return val.sort((a, b) => compareFn(a[1], b[1]))
  }
}

function putKeyAtTheEnd(key: string) {
  return <K, V>(val: Entries<K, V>): Entries<K, V> => {
    const otherIndex = val.findIndex(([k]) => k === key)
    const other = val[otherIndex]
    if (otherIndex > -1) {
      val.splice(otherIndex, 1)
      return val.concat([other]) as Entries<K, V>
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
