import * as pcapi from 'repository/pcapi/pcapi'

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
      'Une erreur est survenue lors de l’enregistrement de l’institution'
    )
  })

  it('should return a confirmation when the institutions is saved', async () => {
    jest.spyOn(pcapi, 'patchEducationalInstitution').mockResolvedValueOnce(null)
    const response = await patchEducationalInstitutionAdapter({
      offerId: '12',
      institutionId: '24',
    })
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'L’institution a bien été rattachée à l’offre'
    )
  })
})
