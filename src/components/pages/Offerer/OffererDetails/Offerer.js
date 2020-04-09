export class Offerer {
  constructor(offerer = {}, adminUserOfferer) {
    this.address = offerer.address || ''
    this.adminUserOfferer = adminUserOfferer
    this.bic = offerer.bic || ''
    this.city = offerer.city || ''
    this.iban = offerer.iban || ''
    this.id = offerer.id
    this.name = offerer.name || ''
    this.postalCode = offerer.postalCode || ''
    this.siren = offerer.siren || ''
  }

  get areBankInformationProvided () {
    return !!(this.bic && this.iban)
  }
}
