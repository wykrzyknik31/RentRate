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

### Module not found: Can't resolve 'i18next' (Windows + OneDrive)

If you encounter the error `Module not found: Can't resolve 'i18next'` when running the dev server, especially on Windows with OneDrive sync enabled, this is a known issue with Turbopack's file watcher and Windows file system operations.

**Solution implemented in this project:**

The project uses a React Context Provider pattern for i18n initialization instead of side-effect imports. This ensures proper module resolution across different environments.

**If you still experience issues:**

1. **Clear the Next.js cache:**
   ```bash
   rm -rf .next
   npm run dev
   ```

2. **Ensure dependencies are installed:**
   ```bash
   npm install
   ```

3. **If using OneDrive or other cloud sync:**
   - Consider moving the project to a non-synced directory
   - Or exclude the `node_modules` and `.next` folders from cloud sync
   - Windows OneDrive can cause file locking issues with rapid file changes

4. **Alternative: Use standard Next.js build (without Turbopack):**
   ```bash
   npm run dev -- --no-turbopack
   ```

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
