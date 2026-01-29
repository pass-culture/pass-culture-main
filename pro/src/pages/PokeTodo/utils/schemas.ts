import { z } from 'zod'

import {
  zCreatePokeTodoBodyModel,
  zUpdatePokeTodoBodyModel,
} from '@/apiClient/hey-api/zod.gen'

const formDatetimeField = z
  .union([z.string().min(1), z.null()])
  .optional()
  .default(null)

function validatePriorityDueDateRules(
  data: { priority?: string | null; dueDate?: string | null },
  ctx: z.RefinementCtx
): void {
  if (data.priority === 'high' && !data.dueDate) {
    ctx.addIssue({
      code: 'custom',
      message: 'Due date is required for high-priority todos',
      path: ['dueDate'],
      input: data,
    })
  }

  if (data.dueDate && data.priority === 'low') {
    ctx.addIssue({
      code: 'custom',
      message: 'Low-priority todos cannot have a due date',
      path: ['priority'],
      input: data,
    })
  }
}

function validateDescription(
  data: { isCompleted?: boolean | null; description?: string | null },
  ctx: z.RefinementCtx
): void {
  if (data.isCompleted && !data.description) {
    ctx.addIssue({
      code: 'custom',
      message: 'Description is required when completing a todo',
      path: ['description'],
      input: data,
    })
  }
}

export const NewTodoFormValuesSchema = zCreatePokeTodoBodyModel
  .extend({ dueDate: formDatetimeField })
  .superRefine((data, ctx) => {
    validatePriorityDueDateRules(data, ctx)
  })

export type NewTodoFormValues = z.output<typeof NewTodoFormValuesSchema>
export type NewTodoFormInput = z.input<typeof NewTodoFormValuesSchema>

export const EditedTodoFormValuesSchema = zUpdatePokeTodoBodyModel
  .extend({ dueDate: formDatetimeField })
  .superRefine((data, ctx) => {
    validateDescription(data, ctx)
    validatePriorityDueDateRules(data, ctx)
  })

export type EditedTodoFormValues = z.output<typeof EditedTodoFormValuesSchema>
export type EditedTodoFormInput = z.input<typeof EditedTodoFormValuesSchema>
