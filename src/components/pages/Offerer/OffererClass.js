export class OffererClass {
  constructor(id, siren, name, address, bic, iban, adminUserOfferer) {
    this.id = id
    this.siren = siren
    this.name = name
    this.address = address
    this.bic = bic
    this.iban = iban
    this.adminUserOfferer = adminUserOfferer
  }

  isIdOrNameDefined = () => !!(this.id || this.name)

  areBankInformationProvided = () => !!(this.bic && this.iban)
}
