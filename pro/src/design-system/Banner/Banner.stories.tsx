import type { StoryObj } from '@storybook/react-vite'
import { Banner, BannerVariants } from './Banner'
import fullLinkIcon from '@/icons/full-link.svg'
import turtle from '../assets/turtle.png'
import { withRouter } from 'storybook-addon-remix-react-router'

export default {
  title: '@/design-system/Banner',
  component: Banner,
  decorators: [
    withRouter,
    (Story: any) => (
      <div style={{ width: 'fit-content' }}>
        <Story />
      </div>
    ),
  ],
}

export const Default: StoryObj<typeof Banner> = {
  args: {
    title: 'Titre important très long très long très long très long très',
    description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mattis libero ultrices sem scelerisque gravida. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",
    actions: [
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon, type: 'link' },
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon, type: 'link' },
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon, type: 'link' },
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon, type: 'link' },
    ],
    imageSrc: turtle,
    variant: BannerVariants.DEFAULT,
    size: 'default',
    closable: true,
  },
}

export const WithSuccessVariant: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    variant: BannerVariants.SUCCESS,
  },
}

export const WithWarningVariant: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    variant: BannerVariants.WARNING,
  },
}

export const WithErrorVariant: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    variant: BannerVariants.ERROR,
  },
}

export const WithoutDescription: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    description: undefined,
  },
}

export const WithoutActions: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    actions: [],
  },
}

export const WithoutImage: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    imageSrc: undefined,
  },
}

export const WithoutCloseButton: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    closable: false,
  },
}

export const LargeSize: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    size: 'large',
  },
}

export const CustomIcon: StoryObj<typeof Banner> = {
  args: {
    ...Default.args,
    icon: fullLinkIcon,
  },
}
