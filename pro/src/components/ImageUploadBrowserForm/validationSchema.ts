import * as yup from 'yup'

import { Constraint } from 'components/ConstraintCheck/imageConstraints'

interface GetValidationSchemaArgs {
  constraints: Constraint[]
}

const getValidationSchema = ({ constraints }: GetValidationSchemaArgs) => {
  return yup.object().shape(
    constraints.reduce((acc: any, constraint: Constraint) => {
      return {
        ...acc,
        [constraint.id]: yup.mixed().test({
          message: constraint.description,
          test: async (_image, context: yup.TestContext) =>
            constraint.asyncValidator(context.parent.image),
        }),
      }
    }, {})
  )
}

export default getValidationSchema
