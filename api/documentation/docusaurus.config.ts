import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type * as Redocusaurus from 'redocusaurus';

const env = process.env['ENV'];

const getOpenAPIJsonUrlFromEnv = (): string => {
  if (env === 'testing' || env === 'staging') {
    return `https://backend.${env}.passculture.team/openapi.json`;
  }
  if (env === 'integration') {
    return 'https://backend.staging.passculture.team/openapi.json';
  }
  if (env === 'production') {
    return 'https://backend.passculture.pro/openapi.json';
  }
  return 'http://localhost:5001/openapi.json';
}

const getDocumentationBaseUrlFromEnv = (): string => {
  if (env === 'testing' || env === 'staging') {
    return `https://developers.${env}.passculture.team`;
  }
  if (env === 'integration') {
    return 'developers.staging.passculture.team';
  }
  if (env === 'production') {
    return 'https://developers.passculture.pro';
  }
  return 'http://localhost:3000';
}


const config: Config = {
  title: 'API documentation',
  tagline: '',
  favicon: 'img/favicon.ico',
  url: getDocumentationBaseUrlFromEnv(),
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  trailingSlash: false,
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
          primaryColor: '#320096',
        },
      },
    ] satisfies Redocusaurus.PresetEntry,
  ],

  themeConfig: {
    image: 'img/pass-culture-social-card.jpg',
    colorMode: {
      disableSwitch: true,
    },
    navbar: {
      title: 'pass Culture Developers',
      logo: {
        alt: 'pass Culture Logo',
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
          title: 'pass Culture websites',
          items: [
            {
              label: 'For cultural partners',
              href: 'https://passculture.pro/accueil',
            },
            {
              label: 'For beneficiaries',
              href: 'https://passculture.app/accueil',
            },
            {
              label: 'General information',
              href: 'https://pass.culture.fr/',
            },
          ],
        },
        {
          title: 'Useful links',
          items: [
            {
              label: 'CGU',
              href: 'https://www.notion.so/passcultureapp/Conditions-G-n-rales-d-Utilisation-des-API-pass-Culture-ed6df4e66ed048e292350285319e6d2a',
            },
            {
              label: 'Help Center',
              href: 'https://aide.passculture.app/hc/fr',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/pass-culture/pass-culture-main',
            },
          ],
        },
        {
          title: 'Follow us',
          items: [
            {
              label: 'LinkedIn',
              href: 'https://fr.linkedin.com/company/pass-culture',
            },
            {
              label: 'X',
              href: 'https://x.com/pass_Culture',
            },
            {
              label: 'Medium',
              href: 'https://medium.com/passcultureofficiel',
            },
            {
              label: 'TikTok',
              href: 'https://www.tiktok.com/@passcultureofficiel',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} pass Culture. Built with Docusaurus.`,
    },
    prism: {
      additionalLanguages: ['php', 'json', 'bash'],
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
