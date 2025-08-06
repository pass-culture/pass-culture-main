import { CollectiveOfferResponseModel } from '@/apiClient//adage'
import { defaultCollectiveOffer } from '@/commons/utils/factories/adageFactories'

import { getBookableOfferInstitutionAndTeacherName } from '../adageOfferInstitution'

const institution: CollectiveOfferResponseModel['educationalInstitution'] = {
  city: 'Paris',
  id: 1,
  name: 'Victor Hugo',
  postalCode: '75001',
  institutionType: 'Collège',
}

const teacher: CollectiveOfferResponseModel['teacher'] = {
  firstName: 'Prof',
  lastName: 'Sympa',
  civility: 'M.',
  email: 'prof.sympa@sympa.cool',
}

describe('adageOfferInstitution', () => {
  describe('getBookableOfferInstitutionAndTeacherName', () => {
    it('should return the offer institution and teacher names', () => {
      const institutionText = getBookableOfferInstitutionAndTeacherName({
        ...defaultCollectiveOffer,
        educationalInstitution: institution,
        teacher: teacher,
      })

      expect(institutionText).toEqual('Prof Sympa - Collège Victor Hugo')
    })

    it("should not return the teacher name if it's not available", () => {
      const institutionText = getBookableOfferInstitutionAndTeacherName({
        ...defaultCollectiveOffer,
        educationalInstitution: institution,
        teacher: undefined,
      })

      expect(institutionText).toEqual('Collège Victor Hugo')
    })

    it('should not return anything if the institution is not available', () => {
      const institutionText = getBookableOfferInstitutionAndTeacherName({
        ...defaultCollectiveOffer,
        educationalInstitution: undefined,
        teacher: teacher,
      })

      expect(institutionText).toEqual(null)
    })
  })
})
