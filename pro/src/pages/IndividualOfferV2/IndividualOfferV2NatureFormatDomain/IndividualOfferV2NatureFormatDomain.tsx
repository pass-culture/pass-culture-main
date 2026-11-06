import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { type FormatEnum, NatureEnum } from '@/apiClient/v1'
import { GET_NFD_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setFormat, setNature } from '@/commons/store/nfd/reducer'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import strokeBookIcon from '@/icons/stroke-book.svg'
import strokeCardsIcon from '@/icons/stroke-cards.svg'
import strokeEventsIcon from '@/icons/stroke-events.svg'
import strokeNumIcon from '@/icons/stroke-num.svg'
import strokeRightIcon from '@/icons/stroke-right.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './IndividualOfferV2NatureFormatDomain.module.scss'

const natureIcon: Record<NatureEnum, string> = {
  [NatureEnum.BIEN]: strokeBookIcon,
  [NatureEnum.CARTE_ABONNEMENT]: strokeCardsIcon,
  [NatureEnum.EVENEMENT]: strokeEventsIcon,
  [NatureEnum.NUMERIQUE]: strokeNumIcon,
}

type NatureFormatFormValues = {
  nature: NatureEnum
  format: FormatEnum
}

const IndividualOfferV2NatureFormatDomain = (): JSX.Element => {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const nfdQuery = useSWR([GET_NFD_QUERY_KEY], () =>
    api.getNatureFormatDomain()
  )
  const { nature: selectedNature, format: selectedFormat } = useAppSelector(
    (state) => state.nfd
  )

  const form = useForm<NatureFormatFormValues>({
    defaultValues: { nature: selectedNature, format: selectedFormat },
  })
  const nature = form.watch('nature')
  const format = form.watch('format')

  const onSubmit = async (values: NatureFormatFormValues) => {
    dispatch(setNature(values.nature))
    dispatch(setFormat(values.format))
    await navigate('/offre/individuelle/v2/creation/description')
  }

  if (!nfdQuery.data) {
    return <Spinner />
  }

  const natures = nfdQuery.data
  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <MandatoryInfo />
        <FormLayout>
          <FormLayout.Section title="Nature et format">
            <FormLayout.Row lgSpaceAfter>
              <RadioButtonGroup
                name="nature"
                label="Sélectionnez la nature"
                variant="detailed"
                display="horizontal"
                sizing="hug"
                error={form.formState.errors.nature?.message}
                options={natures.map((item) => ({
                  ...form.register('nature', {
                    required: 'Veuillez sélectionner une nature',
                    onChange: () => {
                      form.reset({ nature: form.getValues('nature') })
                    },
                  }),
                  label: item.label,
                  value: item.name,
                  checked: nature === item.name,
                  asset: {
                    variant: 'icon',
                    src: natureIcon[item.name],
                  },
                }))}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              {nature && (
                <div className={styles['format']}>
                  <RadioButtonGroup
                    name="format"
                    label="Sélectionnez le format"
                    variant="detailed"
                    display="horizontal"
                    sizing="hug"
                    error={form.formState.errors.format?.message}
                    options={
                      natures
                        .find((item) => item.name === nature)
                        ?.formats.map((item) => ({
                          ...form.register('format', {
                            required: 'Veuillez sélectionner un format',
                          }),
                          sizing: 'hug',
                          label: item.label,
                          value: item.format,
                          checked: format === item.format,
                        })) ?? []
                    }
                  />
                </div>
              )}
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
        <ActionsBarSticky hasSideNav={false} isEmbedded={true}>
          <ActionsBarSticky.Left>
            <Button
              as="router-link"
              to="/accueil"
              color={ButtonColor.NEUTRAL}
              variant={ButtonVariant.SECONDARY}
              label="Annuler et quitter"
            />
          </ActionsBarSticky.Left>

          <ActionsBarSticky.Right>
            <Button
              type="submit"
              color={ButtonColor.BRAND}
              variant={ButtonVariant.PRIMARY}
              label="Étape suivante"
              icon={strokeRightIcon}
              iconPosition={IconPositionEnum.RIGHT}
            />
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      </form>
    </FormProvider>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2NatureFormatDomain
