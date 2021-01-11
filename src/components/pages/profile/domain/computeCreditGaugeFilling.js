export const computeCreditGaugeFilling = (remainingCredit, creditLimit) => {
  if (creditLimit <= 0) {
    return 0
  }

  const ratio = (10 * remainingCredit) / creditLimit
  return Math.floor(ratio)
}
