/**
 * Pretty-prints the cross-referenced results to stdout with ANSI colors
 * (auto-disabled when stdout is not a TTY or `NO_COLOR` is set) and returns
 * the appropriate exit code.
 */

import { styleText } from 'node:util'

import { formatLocation } from './paths.js'

/**
 * Renders the report. Returns `0` when nothing was found, `1` otherwise.
 */
export function printResults({
  unusedReports,
  nonExistentReports,
  parseErrors,
  unusedCount,
  nonExistentCount,
  moduleCount,
  sourceCount,
  durationMs,
}) {
  for (const report of unusedReports) {
    console.info(styleText('cyan', formatLocation(report.filePath)))
    for (const item of report.unused) {
      console.info(
        `  ${styleText('red', `.${item.className}`)} ${styleText('dim', `(line ${item.line})`)} is unused`
      )
    }
    console.info('')
  }

  for (const report of nonExistentReports) {
    console.info(styleText('cyan', formatLocation(report.filePath)))
    for (const item of report.nonExistent) {
      console.info(
        `  ${styleText('red', `.${item.name}`)} is referenced but not defined`
      )
      for (const ref of item.refs) {
        console.info(
          styleText(
            'dim',
            `    referenced by ${formatLocation(ref.caller)}:${ref.line}`
          )
        )
      }
    }
    console.info('')
  }

  for (const report of parseErrors) {
    console.info(
      `${styleText('yellow', 'warn')} could not parse ${formatLocation(report.filePath)}: ${report.parseError.message}`
    )
  }

  console.info(
    `\nScanned ${moduleCount} module files and ${sourceCount} source files in ${durationMs.toFixed(0)} ms.`
  )
  if (unusedCount === 0 && nonExistentCount === 0) {
    console.info(styleText('green', '✓ No unused or unknown CSS classes found!'))
    return 0
  }
  if (unusedCount > 0) {
    console.info(
      styleText(
        'red',
        `✗ ${unusedCount} unused CSS class${unusedCount === 1 ? '' : 'es'}`
      )
    )
  }
  if (nonExistentCount > 0) {
    console.info(
      styleText(
        'red',
        `✗ ${nonExistentCount} reference${nonExistentCount === 1 ? '' : 's'} to undefined class${nonExistentCount === 1 ? '' : 'es'}`
      )
    )
  }
  return 1
}
