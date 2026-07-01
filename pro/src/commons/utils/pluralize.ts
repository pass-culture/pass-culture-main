const getPluralizeFn = (locale: string) => {
  const pluralRules = new Intl.PluralRules(locale)

  return (count: number, singular: string, plural: string) => {
    const grammaticalNumber = pluralRules.select(count)

    return grammaticalNumber === 'one' ? `${singular}` : `${plural}`
  }
}

export const pluralizeFr = getPluralizeFn('fr-FR')
