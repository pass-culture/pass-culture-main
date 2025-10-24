import { Meta, StoryObj } from '@storybook/react'
import { Banner, BannerProps, BannerVariants } from './Banner'
import fullLinkIcon from '@/icons/full-link.svg'
import turtle from '../assets/turtle.png'
import { withRouter } from 'storybook-addon-remix-react-router'

const meta: Meta<BannerProps> = {
  title: '@/design-system/Banner',
  component: Banner,
  decorators: [withRouter],
}
export default meta
type Story = StoryObj<typeof Banner>

export const Default: Story = {
  args: {
    title: 'Titre important très long très long très long très long très',
    description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mattis libero ultrices sem scelerisque gravida. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",
    links: [
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon },
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon },
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon },
      { label: 'En savoir plus', href: '#', icon: fullLinkIcon },
    ],
    imageSrc: turtle,
    variant: BannerVariants.DEFAULT,
    size: 'default',
    closable: true,
  },
}

export const WithSuccessVariant: Story = {
  args: {
    ...Default.args,
    variant: BannerVariants.SUCCESS,
  },
}

export const WithWarningVariant: Story = {
  args: {
    ...Default.args,
    variant: BannerVariants.WARNING,
  },
}

export const WithErrorVariant: Story = {
  args: {
    ...Default.args,
    variant: BannerVariants.ERROR,
  },
}

export const WithoutDescription: Story = {
  args: {
    ...Default.args,
    description: undefined,
  },
}

export const WithoutLinks: Story = {
  args: {
    ...Default.args,
    links: [],
  },
}

export const WithoutImage: Story = {
  args: {
    ...Default.args,
    imageSrc: undefined,
  },
}

export const WithoutCloseButton: Story = {
  args: {
    ...Default.args,
    closable: false,
  },
}

export const LargeSize: Story = {
  args: {
    ...Default.args,
    size: 'large',
  },
}

export const CustomIcon: Story = {
  args: {
    ...Default.args,
    icon: fullLinkIcon,
  },
}
