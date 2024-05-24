import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type * as Redocusaurus from 'redocusaurus';

const getOpenAPIJsonUrlFromEnv = (): string => {
  const env = process.env['ENV'];

  if (env === 'testing') {
    return 'https://backend.testing.passculture.team/openapi.json';
  }

  if (env === 'staging') {
    return 'https://backend.staging.passculture.team/openapi.json';
  }

  if (env === 'production') {
    return 'https://backend.passculture.pro/openapi.json';
  }

  return 'http://localhost/openapi.json';
}


const getDocumentationBaseUrlFromEnv = (): string => {
  const env = process.env['ENV'];

  if (env === 'testing') {
    return 'https://developers.testing.passculture.team';
  }

  if (env === 'staging') {
    return 'https://developers.staging.passculture.team';
  }

  if (env === 'production') {
    return 'https://developers.passculture.pro';
  }

  return 'http://localhost:3000';
}
const config: Config = {
  title: 'Pass culture documentation',
  tagline: '',
  favicon: 'img/favicon.ico',


  url: getDocumentationBaseUrlFromEnv(),
  baseUrl: '/',

  organizationName: 'Pass Culture',
  projectName: 'pass-culture-main',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
    // Redocusaurus config
    [
      'redocusaurus',
      {
        specs: [
          {
            spec: getOpenAPIJsonUrlFromEnv(),
            route: '/rest-api/',
          },
        ],
        theme: {
          primaryColor: '#6123df',
        },
      },
    ] satisfies Redocusaurus.PresetEntry,
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'Pass Culture Developers',
      logo: {
        alt: 'Pass Culture Logo',
        src: 'img/passculture_logo.jpeg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'REST API',
          href: '/rest-api/',
        },
        {
          to: '/change-logs',
          label: 'Change logs',
          position: 'left',
        },
        {
          href: 'https://github.com/pass-culture/pass-culture-main',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Tutorial',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'X',
              href: 'https://x.com/pass_Culture',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/pass-culture/pass-culture-main',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Pass Culture. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
