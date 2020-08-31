export const computeCreditGaugeFilling = (remainingCredit, creditLimit) => {
  const ratio = (10 * remainingCredit) / creditLimit
  return Math.floor(ratio)
}
