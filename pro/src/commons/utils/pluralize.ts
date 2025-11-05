const getPluralizeFn = (locale: string) => {
  const frPluralRules = new Intl.PluralRules(locale)

  return (count: number, singular: string, plural: string) => {
    const grammaticalNumber = frPluralRules.select(count)
    switch (grammaticalNumber) {
      case 'one':
        return `${singular}`
      case 'other':
        return `${plural}`
      default:
        throw new Error(`Unknown: ${grammaticalNumber}`)
    }
  }
}

export const pluralizeFr = getPluralizeFn('fr-FR')
