import { useFieldArray, UseFormReturn } from 'react-hook-form'

import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import fullClearIcon from 'icons/full-clear.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import styles from './StocksCalendarFormSpecificTimeSlots.module.scss'

export function StocksCalendarFormSpecificTimeSlots({
  form,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
}) {
  const { fields, remove, append } = useFieldArray({
    name: 'specificTimeSlots',
  })

  return (
    <>
      <div className={styles['time-slots']}>
        {fields.map((timeSlot, index) => (
          <div className={styles['time-slot']} key={timeSlot.id}>
            <TimePicker
              required
              label={`Horaire ${index + 1}`}
              className={styles['time-slot-picker']}
              error={
                form.formState.errors.specificTimeSlots?.[index]?.slot?.message
              }
              {...form.register(`specificTimeSlots.${index}.slot`)}
            />
            {fields.length > 1 && (
              <div className={styles['time-slot-clear']}>
                <Tooltip content={`Supprimer l'horaire ${index + 1}`}>
                  <button
                    type="button"
                    className={styles['time-slot-clear-button']}
                    onClick={() => {
                      remove(index)

                      const nextInput = `specificTimeSlots.${index}.slot`
                      const previousInput = `specificTimeSlots.${index - 1}.slot`

                      //    Focus on the next input if it exists, otherwise focus on the previous input
                      setTimeout(() => {
                        ;(
                          document.querySelector<HTMLInputElement>(
                            `[name="${nextInput}"]`
                          ) ||
                          document.querySelector<HTMLInputElement>(
                            `[name="${previousInput}"]`
                          )
                        )?.focus()
                      })
                    }}
                  >
                    <SvgIcon
                      alt={`Supprimer l'horaire ${index + 1}`}
                      src={fullClearIcon}
                      className={styles['time-slot-clear-button-icon']}
                    ></SvgIcon>
                  </button>
                </Tooltip>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className={styles['add-time-slot']}>
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() => {
            append({ slot: '' })
            const inputToFocus = `specificTimeSlots.${fields.length}.slot`

            // The input we want to focus has not been rendered first
            setTimeout(() => {
              document.getElementById(inputToFocus)?.focus()
            }, 0)
          }}
        >
          Ajouter un horaire
        </Button>
      </div>
    </>
  )
}
