This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Prerequisites

- Node.js 18 or later
- npm (comes with Node.js)

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Troubleshooting

### 'next' is not recognized as an internal or external command

If you see this error when running `npm run dev`, it means the dependencies haven't been installed yet. Follow these steps:

1. **Install dependencies first:**
   ```bash
   npm install
   ```

2. **Then run the development server:**
   ```bash
   npm run dev
   ```

**Alternative solutions if the issue persists:**

- Use `npx` to run Next.js directly:
  ```bash
  npx next dev
  ```

- Verify your Node.js version (must be 18 or later):
  ```bash
  node --version
  ```

- If you have an old version, update Node.js from [nodejs.org](https://nodejs.org)

- Clear npm cache and reinstall:
  ```bash
  npm cache clean --force
  npm install
  ```

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
