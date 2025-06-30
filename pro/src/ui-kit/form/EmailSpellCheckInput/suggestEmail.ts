import emailSpellChecker from '@zootools/email-spell-checker'

const TOP_MOST_USED_DOMAINS = [
  'gmail.com',
  'orange.fr',
  'wanadoo.fr',
  'yahoo.fr',
  'hotmail.fr',
  'free.fr',
  'fnac.com',
  'hotmail.com',
  'outlook.fr',
  'cultura.fr',
]

const config = {
  domainThreshold: 4,
  domains: TOP_MOST_USED_DOMAINS,
  secondLevelDomains: [],
  topLevelDomains: [],
}

export const suggestEmail = (
  email: string,
  fieldHasError: boolean
): string | undefined => {
  if (fieldHasError) {
    return
  }

  return emailSpellChecker.run({ ...config, email })?.full
}
