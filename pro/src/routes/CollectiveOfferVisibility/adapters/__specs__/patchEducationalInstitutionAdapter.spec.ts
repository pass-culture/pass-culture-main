import * as pcapi from 'repository/pcapi/pcapi'

import { CollectiveOfferResponseModel } from 'core/OfferEducational'
import { patchEducationalInstitutionAdapter } from '../patchEducationalInstitutionAdapter'

describe('patchEducationalInstitutionAdapter', () => {
  it('should return an error when the institutions could not be saved', async () => {
    jest.spyOn(pcapi, 'patchEducationalInstitution').mockRejectedValue(null)
    const response = await patchEducationalInstitutionAdapter({
      offerId: '12',
      institutionId: '24',
    })
    expect(response.isOk).toBe(false)
    expect(response.message).toBe(
      'Les paramètres de visibilité de votre offre n’ont pu être enregistrés'
    )
  })

  it('should return a confirmation when the institutions is saved', async () => {
    jest
      .spyOn(pcapi, 'patchEducationalInstitution')
      .mockResolvedValueOnce({} as CollectiveOfferResponseModel) // we do not test the content
    const response = await patchEducationalInstitutionAdapter({
      offerId: '12',
      institutionId: '24',
    })
    expect(response.isOk).toBeTruthy()
  })
})
