export class Offerer {
  constructor(offerer = {}) {
    this.address = offerer.address || ''
    this.apiKey = new ApiKeyType(offerer.apiKey)
    this.bic = offerer.bic || ''
    this.city = offerer.city || ''
    this.iban = offerer.iban || ''
    this.id = offerer.id
    this.name = offerer.name || ''
    this.postalCode = offerer.postalCode || ''
    this.siren = offerer.siren || ''
    this.demarchesSimplifieesApplicationId =
      offerer.demarchesSimplifieesApplicationId || ''
  }

  get areBankInformationProvided() {
    return !!(this.bic && this.iban)
  }

  get formattedSiren() {
    return formatSiren(this.siren)
  }
}

const formatSiren = siren => {
  if (!siren) return ''

  const blocks = []
  for (let i = 0; i < siren.length; i += 3) {
    blocks.push(siren.substr(i, 3))
  }

  return blocks.join(' ')
}

class ApiKeyType {
  constructor(apiKeyResponse) {
    this.maxAllowed = apiKeyResponse ? apiKeyResponse.maxAllowed : ''
    this.savedApiKeys = apiKeyResponse ? apiKeyResponse.prefixes : []
  }
}
