/**
 * Combines per-file module reports and per-file source reports into the two
 * lists the CLI presents:
 *   - `unusedReports`: classes declared in a module but never referenced,
 *   - `nonExistentReports`: `styles.foo` references targeting a class that
 *     does not exist in the imported module.
 *
 * Dynamic accesses (`styles[expr]`) widen the safety net: when any consumer
 * of a given module touches its binding dynamically, both checks for that
 * module are skipped (we cannot prove unused, and we cannot validate the
 * static refs against a name space we do not fully observe).
 */

function emptyUsageBucket() {
  return {
    used: new Map(),
    dynamicConsumers: new Set(),
    nonExistentChecks: [],
  }
}

function buildUsagesByModule(sourceReports) {
  const usagesByModule = new Map()
  for (const sourceReport of sourceReports) {
    if (sourceReport.fileDisabled) continue
    for (const importEntry of sourceReport.imports) {
      const access = sourceReport.accesses.get(importEntry.binding)
      if (!access) continue
      let target = usagesByModule.get(importEntry.modulePath)
      if (!target) {
        target = emptyUsageBucket()
        usagesByModule.set(importEntry.modulePath, target)
      }
      if (access.dynamic) target.dynamicConsumers.add(sourceReport.filePath)
      for (const reference of access.static) {
        const callers = target.used.get(reference.name)
        if (callers) {
          callers.push(sourceReport.filePath)
        } else {
          target.used.set(reference.name, [sourceReport.filePath])
        }
        if (!reference.disabled && !access.dynamic) {
          target.nonExistentChecks.push({
            caller: sourceReport.filePath,
            line: reference.line,
            name: reference.name,
          })
        }
      }
    }
  }
  return usagesByModule
}

/**
 * Cross-references the parsed module and source reports and returns the
 * data needed for the final printout, including parse errors that surfaced
 * while reading a module file.
 */
export function crossReference(moduleReports, sourceReports) {
  const usagesByModule = buildUsagesByModule(sourceReports)
  const unusedReports = []
  const nonExistentReports = []
  const parseErrors = []
  let unusedCount = 0
  let nonExistentCount = 0

  for (const moduleReport of moduleReports) {
    if (moduleReport.parseError) {
      parseErrors.push(moduleReport)
      continue
    }
    if (moduleReport.fileDisabled) continue
    const usage =
      usagesByModule.get(moduleReport.filePath) ?? emptyUsageBucket()
    const dynamic = usage.dynamicConsumers.size > 0
    if (!dynamic) {
      const unused = [...moduleReport.declared]
        .filter(
          ([className]) =>
            !moduleReport.suppressedUnused.has(className) &&
            !usage.used.has(className)
        )
        .map(([className, line]) => ({ className, line }))
      if (unused.length > 0) {
        unusedCount += unused.length
        unusedReports.push({ filePath: moduleReport.filePath, unused })
      }
    }
    const undeclaredChecks = usage.nonExistentChecks.filter(
      (check) => !moduleReport.declared.has(check.name)
    )
    const nonExistentByClass = Map.groupBy(
      undeclaredChecks,
      (check) => check.name
    )
    if (nonExistentByClass.size > 0) {
      nonExistentCount += nonExistentByClass.size
      nonExistentReports.push({
        filePath: moduleReport.filePath,
        nonExistent: [...nonExistentByClass.entries()].map(([name, refs]) => ({
          name,
          refs: refs.map(({ caller, line }) => ({ caller, line })),
        })),
      })
    }
  }

  return {
    unusedReports,
    nonExistentReports,
    parseErrors,
    unusedCount,
    nonExistentCount,
  }
}
