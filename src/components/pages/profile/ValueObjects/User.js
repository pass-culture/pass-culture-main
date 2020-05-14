export default class User {
  constructor(user = {}) {
    this.departementCode = user.departementCode
    this.email = user.email
    this.expenses = user.expenses
    this.firstName = user.firstName
    this.lastName = user.lastName
    this.publicName = user.publicName
    this.wallet_balance = user.wallet_balance
    this.wallet_date_created = user.wallet_date_created
  }
}
