# 📋 Next.js Freelance Templates — Project Review & Specification

**Version:** 1.0  
**Last Updated:** 2026-05-31  
**Audience:** Freelancers deploying templates to clients  
**Status:** Reference Documentation

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Template System Model](#-template-system-model)
3. [Available Templates](#-available-templates)
4. [Architecture & Tech Stack](#-architecture--tech-stack)
5. [Key Decision Records](#-key-decision-records)
6. [Template 01: Service Business (Reference Implementation)](#-template-01-service-business-reference)
7. [Naming Conventions & Terminology](#-naming-conventions--terminology)
8. [Deployment Guide](#-deployment-guide)
9. [UI/UX & SEO Standards](#-uiux--seo-standards)
10. [Checklist for Freelancers](#-checklist-for-freelancers)

---

## 🎯 Project Overview

This workspace provides **production-ready Next.js templates** for freelancers to deploy to clients. Each template is a complete, self-contained business solution with:

- **Public Portfolio Frontend** — Client-facing website at `/`
- **Admin Backend UI** — Content management dashboard at `/admin`
- **Admin Login** — Secure authentication at `/admin/login`
- **Local SQLite Database** — Self-contained data persistence
- **VPS/Docker Deployment** — Full control, persistent filesystem

**Key Principle:** Each client receives a fully deployed instance with Admin login credentials. They manage their own content via the backend UI. No marketplace, no client-side deployment.

---

## 🏗️ Template System Model

### What is a Template?

A **Template** = production-ready Next.js app for a specific business type that:

✅ Freelancer deploys once for each client  
✅ Freelancer sends Admin login to client (no source code)  
✅ Client edits content via Admin Backend UI  
✅ Independent from other templates (no shared components)  

### Delivery Model

```
Developer (You) 
    ↓
   Deploy to VPS/Docker 
    ↓
   Send Admin URL + Login Credentials to Client
    ↓
   Client manages content via Admin Backend UI
```

**NOT a marketplace** — not about selling template source code  
**NOT a boilerplate kit** — each client gets a running instance  

---

## 📦 Available Templates

| Template | Industry | DB | Status | Color Theme | Font |
|---|---|---|---|---|---|
| **portfolio-freelance** | Freelance/Portfolio | SQLite (key-value) | ✅ Complete | — | — |
| **01-service-business** | General Services | Prisma + SQLite | ✅ Reference Impl. | — | — |
| **02-clinic-beauty** | Clinic/Beauty | Prisma + SQLite | ✅ UI Polished | Rose | Raleway |
| **03-restaurant-cafe** | Restaurant/Café | Prisma + SQLite | ✅ UI Polished | Amber | Playfair |
| **04-real-estate** | Real Estate | Prisma + SQLite | ✅ UI Polished | Navy+Gold | Raleway |
| **05-course-coaching** | Courses/Coaching | Prisma + SQLite | ✅ UI Polished | Amber | Raleway |
| **06-corporate** | Corporate/Enterprise | Prisma + SQLite | ✅ UI Polished | Blue | Raleway |
| **07-product-sale** | Retail/E-commerce | Prisma + SQLite | ✅ UI Polished | Red | Raleway |
| **08-booking-service** | Booking Services | Prisma + SQLite | ✅ UI Polished | Violet | Raleway |

---

## 🔧 Architecture & Tech Stack

### Core Technologies

- **Next.js 14+** — React + Server Components + App Router
- **TypeScript** — Type safety throughout
- **Tailwind CSS** — Utility-first styling (no next/font/google)
- **Prisma ORM** — Local schema per template
- **SQLite** — Local database, zero external dependencies
- **Next Auth (Custom)** — Cookie-based sessions, no next-auth library
- **Server Actions** — Form handling, no API routes needed

### Database Layer

Each template has its own **local `prisma/schema.prisma`**:

```
templates/01-service-business/
  └── prisma/
      └── schema.prisma  (User, HeroSection, Service, Review, etc.)

templates/02-clinic-beauty/
  └── prisma/
      └── schema.prisma  (User, Service, Appointment, Gallery, etc.)
```

- **No shared database** — each client instance is independent
- **Self-contained** — SQLite file lives in the deployed directory
- **Migratable** — Prisma migrations create/update schema on startup

### File Upload Handling

All models with images use **two paired fields**:

```typescript
imageUrl: String?          // Path or external URL
imageSourceType: String?   // "url" | "upload"
```

**Admin UI shows tabs:**
- "URL" → direct link (e.g., external CDN)
- "Upload" → local file saved to `/public/uploads/`

---

## 📋 Key Decision Records

### Auth: Custom Cookie Sessions

**Decision:** Use custom `lib/auth.ts` + `User` model (no next-auth)

✅ **Why:** Simpler, fewer dependencies, same pattern as portfolio-freelance  
✅ **Implementation:** Hashed password in DB, cookie session, middleware checks  
✅ **Setup:** Seed first admin user via script or `prisma db seed`

### Deployment: VPS/Docker Only

**Decision:** No Vercel, no serverless

✅ **Why:** SQLite + `/public/uploads/` need persistent filesystem  
✅ **Approach:** Docker container + Docker Compose + volume mounts  
✅ **Backups:** Tar the SQLite file + uploads folder, store offsite

### Image Fields: Dual Strategy

**Decision:** Every image model has `imageUrl + imageSourceType` pair

✅ **Why:** Admin needs to toggle between URL and file upload  
✅ **Admin UI:** Tab control switches input type  
✅ **Storage:** Uploads go to `/public/uploads/`, tracked in DB

### Setup Flow: User Count Lock

**Decision:** If `User.count() === 0`, redirect all routes to `/setup`

✅ **Why:** First-run onboarding, client enters site name + email + password  
✅ **Automation:** Setup creates admin user + seeds `SiteSettings` defaults  
✅ **Reset:** Delete the User row to re-run setup

---

## 🎨 Template 01: Service Business (Reference Implementation)

This is the **canonical template**. All other templates (02–08) follow this pattern.

### Public Frontend Structure

8 scrollable sections for service businesses:

| Section | Model | Purpose |
|---|---|---|
| **Hero** | `HeroSection` | Main headline, CTA |
| **Service Areas** | `ServiceArea[]` | Geographic coverage |
| **Services** | `Service[]` | List of offered services + pricing |
| **Team** | `TeamMember[]` | Staff profiles |
| **Gallery** | `GalleryImage[]` | Work samples |
| **Reviews** | `Review[]` | Client testimonials |
| **FAQ** | `Faq[]` | Common questions |
| **Contact** | `LeadSubmission` | Lead form + contact info |

### Admin Backend UI

Multi-section sidebar form:

```
📋 Admin Dashboard
├── Hero Section (1 editor)
├── Service Areas (add/edit/delete rows)
├── Services (add/edit/delete + image fields)
├── Team (add/edit/delete + image fields)
├── Gallery (upload + manage images)
├── Reviews (add/edit/delete)
├── FAQ (add/edit/delete)
└── Contact Settings (form enable, email address)
```

### Lead Form Behavior

✅ **Immediate save** to `LeadSubmission` table  
✅ **Email notification** via Resend (when API key configured)  
✅ **Code is ready** in `app/actions/lead.ts` — just uncomment + add env vars

### SEO Defaults

All defaults are **production-ready keywords** (not template filler):

❌ BAD: "Edit this hero title" / "Our Service Business"  
✅ GOOD: "รับสร้างเว็บไซต์ ครบจบในที่เดียว"

**`generateMetadata()`** reads from SQLite → ensures title/description stay in sync with Admin edits

---

## 📖 Naming Conventions & Terminology

| Term | Definition | Use Instead Of |
|---|---|---|
| **Template** | Pre-built Next.js app for one business type | boilerplate, theme |
| **Public Frontend** | Client-facing website at `/` | frontend, website |
| **Admin Backend UI** | Dashboard at `/admin` for content editing | admin, CMS, backend |
| **Landing Content** | Editable text/images/settings in DB | page data, content |
| **SQLite Content Store** | Local SQLite database for Landing Content | database, storage |
| **Admin Session** | Cookie session proving admin is logged in | auth token, JWT |
| **Server Action** | Next.js server function for form submit | API endpoint, RPC |
| **Reference Implementation** | Template 01 that sets the pattern | MVP, prototype |
| **Image Field Pair** | `imageUrl + imageSourceType` together | image field, image URL |

### When Speaking to Clients:

- "Your **Portfolio Frontend** is at [domain]"
- "You manage content in your **Admin Backend UI** at [domain]/admin"
- "Your **Landing Content** (title, images, testimonials) is stored in your database"

---

## 🚀 Deployment Guide

### Pre-Deployment Checklist

```bash
# 1. Environment Setup
cp .env.example .env
# Fill in:
#   - DATABASE_URL=file:./data/portfolio.db (or your path)
#   - RESEND_API_KEY=... (for lead email, optional)
#   - NODE_ENV=production

# 2. Install dependencies
npm install

# 3. Run Prisma migrations
npm run db:migrate

# 4. Seed initial admin user
npm run db:seed
# Or manually create via /setup route

# 5. Build
npm run build

# 6. Test production build
npm run start
```

### Docker Deployment (Recommended)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**docker-compose.yml:**

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: file:/app/data/portfolio.db
    volumes:
      - ./data:/app/data           # SQLite persists
      - ./public/uploads:/app/public/uploads  # User uploads persist
    restart: unless-stopped
```

### VPS Deployment Steps

1. **SSH to VPS** → create app directory
2. **Git clone** template repo
3. **Docker build & run**
4. **Nginx reverse proxy** to localhost:3000
5. **SSL cert** (Let's Encrypt)
6. **Backup script** for `/data/` and `/public/uploads/`

### Client Handoff Checklist

- [ ] Admin URL + HTTPS working
- [ ] First admin user created (email + password)
- [ ] Sample content pre-filled (hero title, 1 service, 1 review)
- [ ] Contact form tested
- [ ] Upload folder writable (permissions: 755)
- [ ] Backup strategy documented
- [ ] Client trained on Admin UI basics

---

## 🎨 UI/UX & SEO Standards

### Font Stack

```css
/* Use this across all templates */
font-family: Inter, "Noto Sans Thai", "Segoe UI", Arial, sans-serif;
```

❌ **Don't use** `next/font/google` in dev/build → network issues in restricted environments  
✅ **Use** system fonts + fallbacks in CSS

### Hero Visual

- ✅ Floating cards showing skills/badges
- ✅ Subtle animations (scroll reveal, hover lift)
- ✅ Professional, not demo-like
- ❌ NO spinning cubes, NO abstract art that says "this is a template"

### Service Section

- ✅ Dynamic headings from DB ("บริการของเรา")
- ✅ Price labels: "เริ่มต้น ฿5,000"
- ✅ Remove friction for client inquiry
- ❌ NO placeholder text like "Our Services" or generic descriptions

### Content Guidelines

**Hero Title (default):** Must be searchable keyword, not template placeholder

```
❌ "Welcome to Service Business"
✅ "รับทำเว็บไซต์ ครบจบในที่เดียว"

❌ "Your Freelance Portfolio"
✅ "ธีรภัทร เตโช · Full Stack Developer"
```

### Long-Form Landing Page

Minimum sections for credibility:

1. Hero + value prop
2. Trust metrics (years exp, projects done, clients)
3. Selected work/portfolio
4. Services + pricing
5. Workflow/process
6. Testimonials/social proof
7. FAQ
8. Contact/CTA

❌ NOT a short hero page  
✅ "Marketing funnel" for selling your services

### Animations

Keep it professional:

- ✅ Image zoom on hover
- ✅ Fade-in on scroll
- ✅ Card lift on hover
- ✅ Floating elements
- ❌ Auto-playing video
- ❌ 3D transforms
- ❌ Anything that looks like "this is a demo"

---

## ✅ Checklist for Freelancers

### Before Deploying to Client

- [ ] Template builds locally: `npm run build` succeeds
- [ ] All images load (no 404s)
- [ ] Admin login works with test credentials
- [ ] Admin form submit saves to SQLite
- [ ] Image upload saves to `/public/uploads/`
- [ ] Contact form (if enabled) captures submissions
- [ ] Default content displays on Public Frontend
- [ ] Mobile responsive checked (375px, 768px, 1024px)
- [ ] SEO meta tags render (check source)
- [ ] No console errors in browser DevTools

### Environment Variables Checklist

```bash
# Required
DATABASE_URL=file:./data/portfolio.db
NEXTAUTH_SECRET=<random-string>

# Optional but recommended
RESEND_API_KEY=<from-resend.com>
SITE_URL=https://client-domain.com
```

### Docker Build Checklist

- [ ] `docker build` succeeds
- [ ] `docker run -p 3000:3000` starts container
- [ ] Container can write to `/app/data/` (SQLite)
- [ ] Container can write to `/app/public/uploads/`
- [ ] Networking test: curl localhost:3000 returns HTML

### Client Handoff Checklist

- [ ] Admin credentials written down (securely shared)
- [ ] Admin UI walkthrough recorded or documented
- [ ] Client can edit hero title, save, see it live
- [ ] Client can upload an image, see it on frontend
- [ ] Contact form tested (if applicable)
- [ ] Backup instructions provided
- [ ] Support contact info shared (your email/phone)

### Post-Launch

- [ ] Monitor first week for bugs
- [ ] Check SQLite backups running
- [ ] Follow up with client in 2 weeks
- [ ] Offer paid features if requested (e.g., email campaigns, booking integrations)

---

## 🔐 Security Checklist

- [ ] Admin password hashed (bcrypt)
- [ ] Session cookie secure + httpOnly + sameSite
- [ ] NEXTAUTH_SECRET is random (32+ chars)
- [ ] Form validation server-side (zod schemas)
- [ ] File upload restricted to images only
- [ ] File upload size limit (e.g., 5MB)
- [ ] HTTPS in production (Let's Encrypt)
- [ ] Database backups stored offsite
- [ ] No API keys in git (use .env)

---

## 📞 Support & Questions

### Common Issues

**Q: SQLite file is getting large**  
A: Normal. Run `VACUUM;` via `prisma studio` or direct SQL.

**Q: Admin login keeps redirecting to /setup**  
A: Check User table is not empty: `npx prisma studio` → Users table.

**Q: Images not showing after upload**  
A: Check `/public/uploads/` directory has write permission (755), and `imageSourceType` in DB is "upload".

**Q: Can I deploy to Vercel?**  
A: ❌ No. SQLite + file uploads need persistent storage. Use VPS/Docker.

**Q: Can I add my own features?**  
A: ✅ Yes. These are **your templates**. Modify freely, but:
- Maintain the Admin/Public separation
- Keep Image fields as `imageUrl + imageSourceType` pair
- Document changes in CONTEXT.md

---

## 📚 File Structure Reference

```
templates/01-service-business/
├── app/
│   ├── page.tsx                 # Public Frontend home
│   ├── admin/
│   │   ├── page.tsx            # Admin Dashboard
│   │   ├── login/
│   │   │   └── page.tsx        # Admin Login
│   │   └── actions/            # Server Actions for admin forms
│   └── actions/
│       └── lead.ts             # Lead form submission
├── lib/
│   ├── db.ts                   # Database fetch functions
│   ├── auth.ts                 # Auth logic (login, session check)
│   ├── upload.ts               # Image upload handler
│   └── validation.ts           # Zod schemas
├── prisma/
│   └── schema.prisma           # Prisma schema (unique per template)
├── public/
│   └── uploads/                # User-uploaded images
├── .env.example                # Env var template
└── CONTEXT.md                  # Project-specific docs
```

---

## 🎯 Final Notes for Freelancers

1. **Each client gets their own instance** — not a shared multi-tenant app
2. **You keep the code** — client can't request source code, just the running instance
3. **Branding opportunity** — Add your footer/about link for lead generation
4. **Upsell potential** — Once live, offer "add booking system," "email campaigns," etc.
5. **Easy to maintain** — Bug fixes apply to all future clients of that template

---

**Last Updated:** 2026-05-31  
**Maintained By:** IQ (ธีรภัทร เตโช)  
**Contact:** qqkiller.programmer.myself.2006@gmail.com
