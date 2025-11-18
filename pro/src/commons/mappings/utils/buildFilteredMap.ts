export function buildFilteredMap(
  _enum: Record<string, string>,
  _mappings: Record<string, string>
) {
  // Checks if keys between backend model and frontend mappings are exactly the same (it will throw if not)
  checkMappings(_enum, _mappings)

  // Sort mappings by alphabetical order, except "OTHER" (if present) which should always be at the end
  const compareFn = new Intl.Collator('fr-FR').compare
  const sorted = Object.entries(_mappings).toSorted((a, b) =>
    compareFn(a[1], b[1])
  )

  // Eventually move "OTHER" (if present) to the end
  const otherIndex = sorted.findIndex(([key]) => key === 'OTHER')
  const other = sorted[otherIndex]
  const sortedWithOther =
    otherIndex > -1 ? sorted.toSpliced(otherIndex, 1).concat([other]) : sorted

  // Transform into select options list
  return Object.fromEntries(sortedWithOther)
}

/**
 * Internal utils functions
 */

function checkMappings(
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
