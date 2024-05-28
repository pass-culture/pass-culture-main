import * as yup from 'yup'

import { Constraint } from 'components/ConstraintCheck/imageConstraints'

interface GetValidationSchemaArgs {
  constraints: Constraint[]
}

export const getValidationSchema = ({
  constraints,
}: GetValidationSchemaArgs) => {
  return yup.object().shape(
    constraints.reduce((acc: any, constraint: Constraint) => {
      return {
        ...acc,
        [constraint.id]: yup.mixed().test({
          message: constraint.description,
          test: (_image, context: yup.TestContext) =>
            constraint.asyncValidator(context.parent.image),
        }),
      }
    }, {})
  )
}
