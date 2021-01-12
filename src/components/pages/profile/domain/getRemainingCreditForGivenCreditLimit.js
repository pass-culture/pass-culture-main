export const getRemainingCreditForGivenCreditLimit = walletBalance => ({
  current: expenses,
  limit: creditLimit,
}) => {
  const absoluteRemainingCredit = creditLimit - expenses
  return Math.min(walletBalance, absoluteRemainingCredit)
}
