import type { Accept } from 'react-dropzone'

const FILE_SIZE_UNITS = ['byte', 'kilobyte', 'megabyte', 'gigabyte']

/**
 * Formats a size in bytes with French units, in base 1000
 * (e.g. `5_000_000` → "5 Mo").
 */
export function formatFileSize(bytes: number): string {
  let size = bytes
  let unitIndex = 0

  while (size >= 1000 && unitIndex < FILE_SIZE_UNITS.length - 1) {
    size /= 1000
    unitIndex++
  }

  return (
    new Intl.NumberFormat('fr-FR', {
      style: 'unit',
      unit: FILE_SIZE_UNITS[unitIndex],
      maximumFractionDigits: 1,
    })
      .format(size)
      // Intl uses a narrow no-break space, tighter than in the design.
      .replace(/\s/g, ' ')
  )
}

/**
 * Builds the help text describing the accepted formats and the maximum size
 * (e.g. "Formats acceptés : PNG, JPEG, PDF. Poids maximum : 5 Mo.").
 */
export function getConditionsText(accept?: Accept, maxSize?: number): string {
  const conditions: string[] = []

  const extensions = new Set(
    Object.values(accept ?? {})
      .flat()
      .map((extension) => extension.replace(/^\./, '').toUpperCase())
  )
  if (extensions.size > 0) {
    conditions.push(`Formats acceptés : ${[...extensions].join(', ')}.`)
  }

  if (maxSize !== undefined) {
    conditions.push(`Poids maximum : ${formatFileSize(maxSize)}.`)
  }

  return conditions.join(' ')
}
