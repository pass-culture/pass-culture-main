export function formatCount(count: number): string {
  if (count < 1000) {
    return count.toString()
  }

  const countInThousands = Math.round(count / 100) / 10
  const formattedCount = new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  }).format(countInThousands)

  return `${formattedCount} k`
}
