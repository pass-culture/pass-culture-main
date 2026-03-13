import { z } from 'zod'

import { zUserIdentityBodyModel } from '@/apiClient/hey-api/zod.gen'

export const userIdentitySchema = zUserIdentityBodyModel.extend({
  firstName: z.string().trim().pipe(zUserIdentityBodyModel.shape.firstName),
  lastName: z.string().trim().pipe(zUserIdentityBodyModel.shape.lastName),
})
