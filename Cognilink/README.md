# CogniLink - Intelligent Bookmark and Knowledge Management System

CogniLink is a powerful client-side bookmark and knowledge management system that runs entirely in the browser and uses IndexedDB for data storage.

## Project Description

This project is implemented as part of the course requirements.
The repository contains source code and materials related to the CogniLink project.

## Notes

This repository is intended for **educational purposes only**.

## Disclaimer

This project is not intended as a research prototype or a production system.

## Features

- 📚 **Intelligent Bookmark Management** - Add, edit, delete, and organize bookmarks
- 🔍 **Full-Text Search** - High-performance full-text search via a custom inverted index
- 🏷️ **Tag System** - Categorize and organize bookmarks with tags
- 📁 **Category Management** - Create and manage bookmark categories
- ⭐ **Favorites** - Mark and filter favorite bookmarks
- 📦 **Archiving** - Archive bookmarks that are no longer needed
- 💾 **Client-Side Storage** - All data is stored in the browser via IndexedDB
- 🎨 **Modern UI** - A clean, responsive user interface

## Tech Stack

- **React 18+** - UI framework
- **TypeScript** - Type safety and maintainability
- **IndexedDB** - Client-side persistent storage
- **Vite** - Build tool and development server
- **Custom Search Index** - Inverted index–based full-text search implementation

## Project Structure


```
CogniLink/
├── src/
│   ├── components/        # React components
│   │   ├── bookmarks/     # Bookmark-related components
│   │   ├── categories/    # Category-related components
│   │   ├── tags/          # Tag-related components
│   │   ├── search/        # Search-related components
│   │   ├── filters/       # Filtering components
│   │   ├── layout/        # Layout components
│   │   └── ui/            # Shared UI primitives/components
│   ├── contexts/          # React Context
│   ├── db/                # IndexedDB management layer
│   ├── services/          # Business logic services
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── App.tsx            # Main application component
│   └── main.tsx           # Application entry point
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Installation and Running

### Install Dependencies

```bash
npm install
```

### Development Mode

```bash
npm run dev
```

The application will start at http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview the Production Build

```bash
npm run preview
```

## Core Implementation

### 1. IndexedDB Data Management

- Database schema design
- Asynchronous transaction handling
- Data migration support
- Data import/export


### 2. Custom Search Index

- Inverted index implementation
- Chinese/English tokenization
- TF-IDF scoring
- Multi-field search

### 3. React Component Architecture
- 25+ functional components25+
- State management via Context API
- Custom Hooks
- Responsive design

## Data Model

### Bookmark

```typescript
interface Bookmark {
  id: string;
  title: string;
  url: string;
  description?: string;
  notes?: string;
  categoryId?: string;
  tags: string[];
  createdAt: number;
  updatedAt: number;
  favorite: boolean;
  archived: boolean;
}
```

### Category 

```typescript
interface Category {
  id: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  parentId?: string;
  createdAt: number;
  updatedAt: number;
}
```

### Tag

```typescript
interface Tag {
  id: string;
  name: string;
  color?: string;
  createdAt: number;
  usageCount: number;
}
```

## Usage Guide

### Adding a Bookmark

1. Click the “Add Bookmark” button in the top-right corner
2. Fill in the bookmark details (Title and URL are required)
3. Optional: add description, notes, category, and tags
4. Click “Add” to save

### Searching Bookmarks

1. Enter keywords in the top search bar
2. The system searches across title, description, notes, URL, and tags automatically
3. Results are ranked by relevance

### Managing Categories

1. Click the "Categories" tab in the sidebar
2. Click "Add Category" to create a new category
3. Click a category name to filter bookmarks under that category

### Using Tags

1. Enter tags when adding/editing a bookmark
2. Click "Tags" in the sidebar to view all tags
3. Click a tag to filter bookmarks that contain it

### Favorites and Archiving

- Click the star icon on a bookmark card to favorite it
- Archive a bookmark from the bookmark details page
- Use the filter panel to quickly view favorited or archived bookmarks

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT License

## Author

Xihao Yang

---

**⚠️⚠️Caution⚠️⚠️**:  This is a purely client-side application; all data is stored within the browser's IndexedDB. Clearing your browser data will result in the loss of all bookmarks. Please export your data regularly to maintain backups.

