export class OffererClass {
  constructor(id, name, bic, iban, adminUserOfferer) {
    this.id = id
    this.name = name
    this.bic = bic
    this.iban = iban
    this.adminUserOfferer = adminUserOfferer
  }

  isIdOrNameDefined = () => !!(this.id || this.name)

  areBankInformationProvided = () => !!(this.bic && this.iban)
}
