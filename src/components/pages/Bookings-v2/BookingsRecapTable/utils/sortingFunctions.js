export const sortByOfferName = (firstRow, secondRow) => {
  const offerNameOne = firstRow.original.stock.offer_name
  const offerNameTwo = secondRow.original.stock.offer_name
  return offerNameOne.localeCompare(offerNameTwo, 'fr', { sensitivity: 'base' })
}

export const sortByBeneficiaryName = (firstRow, secondRow) => {
  let beneficiaryOne = firstRow.original.beneficiary.lastname
  let beneficiaryTwo = secondRow.original.beneficiary.lastname
  const lastNamesAreTheSame =
    beneficiaryOne.localeCompare(beneficiaryTwo, 'fr', { sensitivity: 'base' }) === 0
  if (lastNamesAreTheSame) {
    beneficiaryOne = firstRow.original.beneficiary.firstname
    beneficiaryTwo = secondRow.original.beneficiary.firstname
  }
  return beneficiaryOne.localeCompare(beneficiaryTwo, 'fr', { sensitivity: 'base' })
}
