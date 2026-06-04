import { ValidationError } from 'yup'

import { ActivityNotOpenToPublic, ActivityOpenToPublic } from 'apiClient/v1/new'
import { activityValidator } from '../activity'

describe('activity', () => {
  it('should sucessfully validate right activity when open to public', async () => {
    const result = await activityValidator(false).validate(
      ActivityOpenToPublic.ART_GALLERY
    )
    expect(result).toBe(ActivityOpenToPublic.ART_GALLERY)
  })

  it('should fail to validate wrong activity when open to public', async () => {
    try {
      await activityValidator(false).validate(
        ActivityNotOpenToPublic.ARTISTIC_COMPANY
      )
    } catch (e) {
      expect(e).toBeInstanceOf(ValidationError)
      expect((e as ValidationError).message).toEqual('Activité non valide')
    }
  })

  it('should sucessfully validate right activity when not open to public', async () => {
    const result = await activityValidator(true).validate(
      ActivityNotOpenToPublic.ARTISTIC_COMPANY
    )
    expect(result).toBe(ActivityNotOpenToPublic.ARTISTIC_COMPANY)
  })

  it('should fail to validate wrong activity when not open to public', async () => {
    try {
      await activityValidator(true).validate(ActivityOpenToPublic.ART_GALLERY)
    } catch (e) {
      expect(e).toBeInstanceOf(ValidationError)
      expect((e as ValidationError).message).toEqual('Activité non valide')
    }
  })
})
