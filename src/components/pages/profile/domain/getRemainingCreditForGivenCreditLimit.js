export const getRemainingCreditForGivenCreditLimit = walletBalance => ({
  current: expenses,
  max: creditLimit,
}) => {
  const absoluteRemainingCredit = creditLimit - expenses
  return Math.min(walletBalance, absoluteRemainingCredit)
}
