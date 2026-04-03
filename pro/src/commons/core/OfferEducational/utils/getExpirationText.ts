import { pluralizeFr } from '@/commons/utils/pluralize'

export function getExpirationText(daysCountBeforeExpiration: number): string {
  if (daysCountBeforeExpiration > 7) {
    return ''
  }

  return `Expire ${
    daysCountBeforeExpiration > 0
      ? `dans ${daysCountBeforeExpiration} ${pluralizeFr(daysCountBeforeExpiration, 'jour', 'jours')}`
      : "aujourd'hui"
  }`
}
