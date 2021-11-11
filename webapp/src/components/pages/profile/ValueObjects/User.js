export default class User {
  constructor(user = {}) {
    this.departementCode = user.departementCode
    this.deposit_version = user.deposit_version
    this.domainsCredit = user.domainsCredit
    this.email = user.email
    this.firstName = user.firstName
    this.id = user.id
    this.pk = user.pk
    this.lastName = user.lastName
    this.publicName = user.publicName
    this.wallet_balance = user.wallet_balance
    this.deposit_expiration_date = user.deposit_expiration_date
    this.isBeneficiary = user.isBeneficiary === undefined ? true : user.isBeneficiary
  }
}
