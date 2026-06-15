import { captureException, withScope } from '@sentry/browser'
import { rootStore } from 'commons/store/store'

import { objectEntries } from '@/commons/utils/object'

export type Entries<K = string, V = string> = [K, V][]

/**
 * Creates a read-only map from a mapping object and an enum-like object.
 * Ensures that the keys of both objects match.
 *
 * @param mappingsObject - The object that maps enum keys to string values. Must have exactly the same keys as `enumObject`.
 * @param enumObject - The enum or object whose keys the mapping must match.
 * @param enumObjectName - Name of the enum object, used in error reporting.
 * @param postProcessPipeline - Optional. An array of functions that process the mapped entries before finalizing the map.
 *
 * @returns {ReadonlyMap<keyof E, M[keyof M]>} A read-only map from the enum keys to mapped values.
 *
 * @remarks If the keys of `mappingsObject` and `enumObject` differ, an error is reported to Sentry (no exception is thrown).
 */
export function createMap<
  M extends Record<keyof E, string>,
  E extends Record<string, string>,
>(
  mappingsObject: M & Record<Exclude<keyof M, keyof E>, never>,
  enumObject: E,
  enumObjectName: string,
  postProcessPipeline: Array<<F extends Entries>(val: F) => F> = []
): ReadonlyMap<keyof E, M[keyof M]> {
  ensureKeysMatchOrReportToSentry(mappingsObject, enumObject, enumObjectName)

  let entries = objectEntries(mappingsObject) as Entries
  for (const postProcess of postProcessPipeline) {
    entries = postProcess(entries)
  }
  return new Map(entries) as unknown as ReadonlyMap<keyof E, M[keyof M]>
}

// TODO (jclery, 2025-11-25):
//  Both `symmetricDifference` and `difference` can be removed once support of `Set.prototype.symmetricDifference` and `Set.prototype.difference` both fit with our own supports rules.
function symmetricDifference(setA: Set<string>, setB: Set<string>) {
  return new Set([...setA, ...setB].filter((x) => !setA.has(x) || !setB.has(x)))
}

function difference(setA: Set<string>, setB: Set<string>) {
  return new Set([...setA].filter((x) => !setB.has(x)))
}

/**
 * Ensures that the keys in `mappingsObject` exactly match those in `enumObject`, and reports any mismatches to Sentry.
 */
function ensureKeysMatchOrReportToSentry<
  M extends Record<keyof E, string>,
  E extends Record<string, string>,
>(
  mappingsObject: M & Record<Exclude<keyof M, keyof E>, never>,
  enumObject: E,
  enumObjectName: string
): void {
  const backEndKeys = new Set(Object.keys(enumObject))
  const frontEndKeys = new Set(Object.keys(mappingsObject))

  const diff = symmetricDifference(backEndKeys, frontEndKeys)

  const backEndExtraKeys = difference(backEndKeys, frontEndKeys)
  const frontEndExtraKeys = difference(frontEndKeys, backEndKeys)

  if (diff.size > 0) {
    notifySentry(
      new Error(
        `[${enumObjectName}] Mismatch keys between back-end and front-end:\n` +
          (backEndExtraKeys.size > 0
            ? `- Following keys are present in ${enumObjectName} back-end model, but not in the front-end mappings list:\n\t${Array.from(backEndExtraKeys.keys()).join(',')}\n`
            : '') +
          (frontEndExtraKeys.size > 0
            ? `- Following keys are present in the front-end mappings list, but not in the ${enumObjectName} back-end model:\n\t${Array.from(frontEndExtraKeys.keys()).join(',')}\n`
            : '')
      )
    )
  }
}

function notifySentry(error: unknown) {
  const isUserImpersonated: boolean | null =
    rootStore.getState().user.currentUser?.isImpersonated ?? null

  withScope((scope) => {
    scope.setContext('default', {
      isUserImpersonated,
    })
    captureException(error)
  })
}
