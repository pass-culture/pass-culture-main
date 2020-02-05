const getRemainingCreditForGivenCreditLimit = walletBalance => ({
  actual: expenses,
  max: creditLimit
}) => {
  const absoluteRemainingCredit = creditLimit - expenses
  const remainingCredit = Math.min(walletBalance, absoluteRemainingCredit)
  return remainingCredit
}

export default getRemainingCreditForGivenCreditLimit
