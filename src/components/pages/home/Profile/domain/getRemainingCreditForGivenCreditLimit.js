export const getRemainingCreditForGivenCreditLimit = walletBalance => ({
  actual: expenses,
  max: creditLimit,
}) => {
  const absoluteRemainingCredit = creditLimit - expenses
  return Math.min(walletBalance, absoluteRemainingCredit)
}
